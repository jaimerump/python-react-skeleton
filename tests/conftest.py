from collections.abc import Iterator

import pytest
from sqlalchemy import Engine, create_engine
from testcontainers.community.postgres import PostgresContainer

from app.lib.models import Base
from app.lib.services.database import DatabaseService


@pytest.fixture(scope="session")
def postgres_container() -> Iterator[PostgresContainer]:
    with PostgresContainer("postgres:16", driver="psycopg") as container:
        yield container


@pytest.fixture(scope="session")
def engine(postgres_container: PostgresContainer) -> Iterator[Engine]:
    engine = create_engine(postgres_container.get_connection_url())
    # Fast unit path: build schema straight from ORM metadata (Alembic round-trips
    # are exercised separately in tests/integration).
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def database_service(engine: Engine) -> DatabaseService:
    # Inject the container engine so services hit real Postgres.
    return DatabaseService(engine=engine)


@pytest.fixture(autouse=True)
def reset_database(engine: Engine) -> Iterator[None]:
    """Per-test isolation without rebuilding the schema: delete every table's rows in
    FK-dependency order after each test."""
    yield
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
