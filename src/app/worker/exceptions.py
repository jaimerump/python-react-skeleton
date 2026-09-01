"""Retry semantics expressed by exception type. The worker's message lifecycle
branches on these:

- success              -> delete message
- NonRetryableJobError -> send to DLQ + delete (no retry loop)
- RetryableJobError    -> leave message (visibility timeout redelivers)
- any other Exception  -> treated as retryable (⚠ a bug can cause infinite redelivery)
"""


class JobError(Exception):
    """Base for all job errors."""


class RetryableJobError(JobError):
    """Transient failure -- do NOT delete the message; let SQS redeliver."""


class NonRetryableJobError(JobError):
    """Permanent failure (bad payload / business rule) -- delete + DLQ, no retry."""


class UnknownJobTypeError(NonRetryableJobError):
    """No handler registered for the job type. Almost always a missing import in
    ``worker/handlers/__init__.py``."""
