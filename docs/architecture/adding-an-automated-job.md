# Adding an automated job — checklist

The job pipeline spans code (and, for scheduled jobs, infrastructure), and **a missing
step doesn't error — it silently no-ops.** Verify the actual side effect, not a green
run.

Two flavors, identical from the queue onward, differing only in **what enqueues the
message**: **on-demand** (application code) vs **scheduled** (a cron rule).

## Shared steps (every job)

1. Add the `job_type` string constant to `src/app/lib/jobs.py` (optionally a Pydantic
   payload schema).
2. Create the handler: subclass `JobHandler`, implement `async def handle(self,
   job_data)`, decorate with `@register_handler("<job_type>")`. Prefer **lazy service
   imports inside `handle`** — the worker health check imports the handler package, so
   heavy top-level imports slow or break startup.
3. **Import the handler module at the bottom of
   `src/app/worker/handlers/__init__.py`.** ⚠ The #1 silent trap: `@register_handler`
   only runs on import — miss this and every message of that type raises
   `UnknownJobTypeError` and goes straight to the DLQ.
4. Raise the right error from `handle`: `NonRetryableJobError` (bad payload /
   business-rule → deleted + DLQ) vs `RetryableJobError` (transient → redelivered).
   ⚠ Any *unexpected* exception is treated as retryable, so a bug can cause infinite
   redelivery.
5. Register required payload fields in `job_router._REQUIRED_FIELDS` so poison messages
   fail early with a clear error.
6. If the job can exceed the SQS visibility timeout (~5 min), add its `job_type` to the
   worker's long-running set (`APP_WORKER_LONG_RUNNING_JOB_TYPES`) so the message isn't
   redelivered mid-run.

## On-demand

Enqueue through the choke point:
`SQSClient.send_message(queue_url_for_job_type(<CONST>), {"job_type": <CONST>, ...})`
— pass ids, not blobs. For user-trackable work, first create a `JobService` row and
thread `job_id` through (`mark_started`/`mark_completed`/`mark_failed`), rolling the row
back if enqueue fails.

⚠ `send_message` returns `None` (no exception) when SQS isn't configured — a 200 API
response is **not** proof the job was queued. Check the return value.

## Scheduled

Add a scheduler rule (e.g. EventBridge `aws_scheduler_schedule`) targeting the SQS queue
with `input = { job_type }`, plus a cadence. ⚠ Then **actually apply the infra to each
environment** — a schedule "in the code" doesn't exist in prod until it's deployed there.

## Feature flags

⚠ Check feature flags in the **service**, not the handler — an off flag makes a job
route and "complete" while doing nothing, indistinguishable from success in the logs.

## Tests (ship with the code)

- Handler happy path + at least one error path + an idempotency guard (jobs can be
  redelivered).
- A service test including the **flag-off no-op**.
- On-demand: assert the enqueued message shape and the enqueue-failure rollback.
