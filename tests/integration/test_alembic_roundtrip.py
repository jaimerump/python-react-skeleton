from collections.abc import Iterator

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect
from testcontainers.community.postgres import PostgresContainer

from app.lib.config import get_settings


@pytest.fixture
def clean_database_url(monkeypatch: pytest.MonkeyPatch) -> Iterator[str]:
    """A dedicated, empty Postgres so real Alembic migrations run from scratch
    (the shared session container already has an ORM-built schema)."""
    with PostgresContainer("postgres:16", driver="psycopg") as container:
        url = container.get_connection_url()
        monkeypatch.setenv("APP_DATABASE_URL", url)
        get_settings.cache_clear()
        yield url
    get_settings.cache_clear()


def test_alembic_upgrade_head_creates_schema(clean_database_url: str) -> None:
    config = Config("alembic.ini")
    command.upgrade(config, "head")

    engine = create_engine(clean_database_url)
    try:
        tables = set(inspect(engine).get_table_names())
    finally:
        engine.dispose()

    assert "jobs" in tables
    assert "alembic_version" in tables
