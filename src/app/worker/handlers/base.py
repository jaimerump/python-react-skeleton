from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from app.worker.exceptions import UnknownJobTypeError

_REGISTRY: dict[str, type["JobHandler"]] = {}


class JobHandler(ABC):
    """Base for job handlers. Prefer LAZY service imports inside ``handle`` -- the
    worker health check imports the handler package, so heavy top-level imports slow
    or break startup."""

    @abstractmethod
    async def handle(self, job_data: dict[str, Any]) -> None: ...


def register_handler(job_type: str) -> Callable[[type[JobHandler]], type[JobHandler]]:
    """Class decorator that registers a handler for a job type. ⚠ Only runs on import,
    so the handler module MUST be imported in ``worker/handlers/__init__.py``."""

    def decorator(cls: type[JobHandler]) -> type[JobHandler]:
        if job_type in _REGISTRY:
            raise ValueError(f"Duplicate handler registration for job_type {job_type!r}")
        _REGISTRY[job_type] = cls
        return cls

    return decorator


def get_handler(job_type: str) -> JobHandler:
    handler_cls = _REGISTRY.get(job_type)
    if handler_cls is None:
        raise UnknownJobTypeError(f"No handler registered for job_type {job_type!r}")
    return handler_cls()


def registered_job_types() -> frozenset[str]:
    return frozenset(_REGISTRY)
