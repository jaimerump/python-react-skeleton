import pytest
from pydantic import ValidationError

from app.lib.config.settings import Settings


def test_settings_compose_every_mixin() -> None:
    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    # A field from each mixin resolves.
    assert settings.database_url
    assert settings.worker_concurrency >= 1
    assert settings.aws_region
    assert settings.pagination_default_limit <= settings.pagination_max_limit


def test_production_requires_dlq_when_queue_set() -> None:
    with pytest.raises(ValidationError):
        Settings(  # type: ignore[call-arg]
            _env_file=None,
            environment="production",
            sqs_queue_url="http://queue",
            sqs_dlq_url=None,
        )


def test_pagination_default_cannot_exceed_max() -> None:
    with pytest.raises(ValidationError):
        Settings(  # type: ignore[call-arg]
            _env_file=None,
            pagination_default_limit=1000,
            pagination_max_limit=10,
        )
