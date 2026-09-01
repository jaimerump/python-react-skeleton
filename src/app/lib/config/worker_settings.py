from pydantic import Field


class WorkerSettingsMixin:
    """Worker polling + concurrency configuration."""

    worker_concurrency: int = Field(default=5, ge=1)
    worker_poll_wait_seconds: int = Field(
        default=20, ge=0, le=20, description="SQS long-poll WaitTimeSeconds (max 20)."
    )
    worker_max_messages_per_poll: int = Field(default=10, ge=1, le=10)
    worker_visibility_timeout_seconds: int = Field(default=300, ge=0)
    worker_heartbeat_seconds: int = Field(default=30, ge=1)
    worker_max_job_depth: int = Field(
        default=25, ge=1, description="Guards against runaway job chains."
    )
    worker_long_running_job_types: frozenset[str] = Field(
        default_factory=frozenset,
        description="Job types allowed to exceed the SQS visibility timeout.",
    )
