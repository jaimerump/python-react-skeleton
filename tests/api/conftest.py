from collections.abc import AsyncGenerator, Iterator

import pytest
import svcs
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.router_registry import mount_all_routers
from app.lib.services.database import DatabaseService


@pytest.fixture
def client(database_service: DatabaseService) -> Iterator[TestClient]:
    """A TestClient over an app wired to the testcontainer DB, bypassing the
    production lifespan's schema-wait (the schema is already built in tests)."""

    @svcs.fastapi.lifespan
    async def test_lifespan(
        app: FastAPI, registry: svcs.Registry
    ) -> AsyncGenerator[None, None]:
        registry.register_value(DatabaseService, database_service)
        yield None

    app = FastAPI(lifespan=test_lifespan)
    mount_all_routers(app)
    with TestClient(app) as test_client:
        yield test_client
