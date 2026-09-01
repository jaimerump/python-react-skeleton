from typing import Any

import pytest

from app.worker import job_router
from app.worker.exceptions import NonRetryableJobError, UnknownJobTypeError
from app.worker.handlers.base import JobHandler, register_handler


def test_parse_invalid_json_is_non_retryable() -> None:
    with pytest.raises(NonRetryableJobError):
        job_router.parse_message_body("not json")


def test_parse_non_object_is_non_retryable() -> None:
    with pytest.raises(NonRetryableJobError):
        job_router.parse_message_body("[1, 2, 3]")


async def test_missing_job_type_is_non_retryable() -> None:
    with pytest.raises(NonRetryableJobError):
        await job_router.route({})


async def test_unknown_job_type_raises() -> None:
    with pytest.raises(UnknownJobTypeError):
        await job_router.route({"job_type": "does_not_exist"})


async def test_missing_required_field_fails_early(monkeypatch: pytest.MonkeyPatch) -> None:
    handled: list[dict[str, Any]] = []

    @register_handler("needs_user")
    class _Handler(JobHandler):
        async def handle(self, job_data: dict[str, Any]) -> None:
            handled.append(job_data)

    monkeypatch.setitem(job_router._REQUIRED_FIELDS, "needs_user", ("user_id",))

    with pytest.raises(NonRetryableJobError):
        await job_router.route({"job_type": "needs_user"})
    assert handled == []  # never reached the handler


async def test_depth_guard_rejects_runaway_chains() -> None:
    with pytest.raises(NonRetryableJobError):
        await job_router.route({"job_type": "anything", "_depth": 10_000})


async def test_registered_handler_is_invoked() -> None:
    handled: list[dict[str, Any]] = []

    @register_handler("echo")
    class _Handler(JobHandler):
        async def handle(self, job_data: dict[str, Any]) -> None:
            handled.append(job_data)

    await job_router.route({"job_type": "echo", "value": 1})
    assert handled == [{"job_type": "echo", "value": 1}]
