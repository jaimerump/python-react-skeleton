from pydantic import Field


class SqsSettingsMixin:
    """SQS transport configuration (shared by api enqueue + worker consume)."""

    sqs_queue_url: str | None = Field(
        default=None,
        description="Primary SQS queue URL. When unset, send_message no-ops (dev/tests).",
    )
    sqs_dlq_url: str | None = Field(
        default=None,
        description="Dead-letter queue URL for non-retryable failures.",
    )
    aws_region: str = Field(default="us-east-1")
    aws_endpoint_url: str | None = Field(
        default=None,
        description="Override endpoint for LocalStack in dev (e.g. http://localhost:4566).",
    )
