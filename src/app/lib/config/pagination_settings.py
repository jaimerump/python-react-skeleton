from pydantic import Field


class PaginationSettingsMixin:
    """Global pagination bounds. Services clamp requested page sizes to these."""

    pagination_default_limit: int = Field(default=50, ge=1)
    pagination_max_limit: int = Field(default=500, ge=1)
