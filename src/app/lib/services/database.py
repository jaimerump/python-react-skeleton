import logging
import time
from collections.abc import Iterator
from contextlib import AbstractContextManager, contextmanager

from sqlalchemy import Engine, create_engine, inspect, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

from app.lib.config import get_settings

logger = logging.getLogger(__name__)


class DatabaseService:
    """Owns the SQLAlchemy engine + session factory.

    Registered as a singleton in the service registry. Tests inject the
    testcontainers engine via the ``engine`` argument.
    """

    def __init__(self, engine: Engine | None = None) -> None:
        self._engine = engine or self._build_engine()
        # expire_on_commit=False keeps ORM objects usable after the session closes,
        # so responses can serialize attributes without re-querying.
        self._session_factory = sessionmaker(
            bind=self._engine, expire_on_commit=False, class_=Session
        )

    @staticmethod
    def _build_engine() -> Engine:
        settings = get_settings()
        return create_engine(
            settings.database_url,
            pool_pre_ping=True,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_recycle=settings.database_pool_recycle_seconds,
            connect_args={
                "options": f"-c statement_timeout={settings.database_statement_timeout_ms}"
            },
        )

    @property
    def engine(self) -> Engine:
        return self._engine

    @contextmanager
    def session_scope(self) -> Iterator[Session]:
        """Transactional scope: commit on success, rollback on error, always close."""
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_db(self) -> Iterator[Session]:
        """FastAPI dependency yielding a request-scoped session."""
        with self.session_scope() as session:
            yield session

    def check_health(self) -> bool:
        try:
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except OperationalError:
            logger.warning("Database health check failed", exc_info=True)
            return False

    def close(self) -> None:
        self._engine.dispose()


class BaseService:
    """Removes session boilerplate for services. Subclasses call
    ``with self._session_context() as session:``."""

    def __init__(self, database_service: DatabaseService) -> None:
        self._database_service = database_service

    def _session_context(self) -> AbstractContextManager[Session]:
        return self._database_service.session_scope()


def wait_for_database_schema(
    database_service: DatabaseService,
    *,
    timeout_seconds: float = 60.0,
    interval_seconds: float = 2.0,
) -> None:
    """Block until the DB is reachable and migrations have run.

    Services depend on a live, migrated database, so the API lifespan calls this
    before registering services. Polls for connectivity and the ``alembic_version``
    table (proof that ``alembic upgrade`` has run).
    """
    deadline = time.monotonic() + timeout_seconds
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with database_service.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                has_version = inspect(conn).has_table("alembic_version")
            if has_version:
                logger.info("Database schema is ready.")
                return
            logger.info("Database reachable but not yet migrated; waiting...")
        except OperationalError as exc:
            last_error = exc
            logger.info("Database not reachable yet; retrying...")
        time.sleep(interval_seconds)
    raise TimeoutError(
        f"Database schema not ready after {timeout_seconds}s"
    ) from last_error
