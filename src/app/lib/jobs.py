"""Job-type constants + the enqueue choke point.

Every enqueue routes through :func:`queue_url_for_job_type` so that splitting the
worker by category later means adding entries to ``_JOB_TYPE_TO_QUEUE`` and
provisioning queues -- not editing call sites. Add advisory Pydantic payload schemas
here alongside each job type.
"""

from app.lib.config import get_settings

# --- job type constants -------------------------------------------------------
# Register new job types here as `SOME_JOB = "some_job"`.

# --- job_type -> queue routing ------------------------------------------------
# Empty today: unmapped job types fall back to the primary queue. When a category
# gets its own queue, map its job types here.
_JOB_TYPE_TO_QUEUE: dict[str, str | None] = {}


def queue_url_for_job_type(job_type: str) -> str | None:
    """Resolve the destination queue for a job type. The single choke point every
    enqueue path must go through. Returns ``None`` when no queue is configured
    (send_message then no-ops -- see SQSClient)."""
    settings = get_settings()
    return _JOB_TYPE_TO_QUEUE.get(job_type) or settings.sqs_queue_url
