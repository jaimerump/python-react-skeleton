import time
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.exc import OperationalError

from app.lib.config import get_settings

# Import models so Base.metadata is complete for autogenerate.
from app.lib.models import Base  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# One source of truth for the DB URL.
config.set_main_option("sqlalchemy.url", get_settings().database_url)

target_metadata = Base.metadata

_MAX_CONNECT_RETRIES = 5
_RETRY_BACKOFF_SECONDS = 2.0


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    connection = _connect_with_retry(connectable)
    with connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


def _connect_with_retry(connectable):
    last_error: Exception | None = None
    for attempt in range(1, _MAX_CONNECT_RETRIES + 1):
        try:
            return connectable.connect()
        except OperationalError as exc:  # e.g. connection exhaustion at startup
            last_error = exc
            if attempt < _MAX_CONNECT_RETRIES:
                time.sleep(_RETRY_BACKOFF_SECONDS * attempt)
    raise RuntimeError("Could not connect to the database for migrations.") from last_error


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
