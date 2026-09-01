"""Dispatch a parsed SQS message to its handler, failing poison messages loudly and
early (before a handler is built)."""

import json
from typing import Any

from app.lib.config import get_settings
from app.worker.exceptions import NonRetryableJobError
from app.worker.handlers import get_handler

# Required payload fields per job type. Poison messages fail here with a clear error
# instead of deep inside a handler. Add an entry when you add a job type.
_REQUIRED_FIELDS: dict[str, tuple[str, ...]] = {}

_DEPTH_KEY = "_depth"


def parse_message_body(body: str) -> dict[str, Any]:
    try:
        data = json.loads(body)
    except json.JSONDecodeError as exc:
        raise NonRetryableJobError(f"Message body is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise NonRetryableJobError("Message body must be a JSON object.")
    return data


async def route(data: dict[str, Any]) -> None:
    job_type = data.get("job_type")
    if not job_type or not isinstance(job_type, str):
        raise NonRetryableJobError("Message is missing a string 'job_type'.")

    _validate_required_fields(job_type, data)
    _guard_job_depth(data)

    handler = get_handler(job_type)  # raises UnknownJobTypeError (non-retryable) if missing
    await handler.handle(data)


def _validate_required_fields(job_type: str, data: dict[str, Any]) -> None:
    missing = [field for field in _REQUIRED_FIELDS.get(job_type, ()) if field not in data]
    if missing:
        raise NonRetryableJobError(
            f"Job {job_type!r} missing required field(s): {', '.join(missing)}"
        )


def _guard_job_depth(data: dict[str, Any]) -> None:
    depth = data.get(_DEPTH_KEY, 0)
    if not isinstance(depth, int) or depth < 0:
        raise NonRetryableJobError(f"Invalid job depth: {depth!r}")
    if depth > get_settings().worker_max_job_depth:
        raise NonRetryableJobError(
            f"Job chain exceeded max depth ({get_settings().worker_max_job_depth})."
        )
