from collections.abc import Iterator

import pytest

from app.worker.handlers import base as handlers_base


@pytest.fixture(autouse=True)
def isolate_handler_registry() -> Iterator[None]:
    """Snapshot and restore the global handler registry so tests that register
    handlers don't leak into each other."""
    snapshot = dict(handlers_base._REGISTRY)
    try:
        yield
    finally:
        handlers_base._REGISTRY.clear()
        handlers_base._REGISTRY.update(snapshot)
