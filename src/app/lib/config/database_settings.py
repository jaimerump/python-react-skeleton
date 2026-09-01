from pydantic import Field


class DatabaseSettingsMixin:
    """Database connection + pool configuration."""

    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/app",
        description="SQLAlchemy database URL (use the psycopg driver).",
    )
    database_pool_size: int = Field(default=5, ge=1)
    database_max_overflow: int = Field(default=10, ge=0)
    database_pool_recycle_seconds: int = Field(default=1800, ge=1)
    database_statement_timeout_ms: int = Field(default=30_000, ge=0)
