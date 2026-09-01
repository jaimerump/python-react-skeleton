from functools import lru_cache
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.lib.config.database_settings import DatabaseSettingsMixin
from app.lib.config.pagination_settings import PaginationSettingsMixin
from app.lib.config.sqs_settings import SqsSettingsMixin
from app.lib.config.worker_settings import WorkerSettingsMixin

Environment = Literal["development", "test", "production"]


class Settings(
    DatabaseSettingsMixin,
    SqsSettingsMixin,
    WorkerSettingsMixin,
    PaginationSettingsMixin,
    BaseSettings,
):
    """Composed application settings.

    ``BaseSettings`` must come LAST so the domain mixins' fields resolve ahead of it
    in the MRO. Read config exclusively through :func:`get_settings` -- never
    ``os.environ`` directly.
    """

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        extra="ignore",
    )

    environment: Environment = "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @model_validator(mode="after")
    def _validate_production_safety(self) -> "Settings":
        if self.is_production and self.sqs_queue_url and not self.sqs_dlq_url:
            raise ValueError(
                "APP_SQS_DLQ_URL must be set in production when a queue is configured."
            )
        if self.pagination_default_limit > self.pagination_max_limit:
            raise ValueError("pagination_default_limit cannot exceed pagination_max_limit.")
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
