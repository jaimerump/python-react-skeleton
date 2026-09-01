import enum

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict


class InputSchema(BaseModel):
    """Base for request bodies (Create/Update). Rejects unknown fields and revalidates
    on assignment."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class ResponseSchema(BaseModel):
    """Base for responses serialized from ORM objects."""

    model_config = ConfigDict(from_attributes=True)


class ErrorCode(enum.StrEnum):
    """Stable, machine-readable error codes. The frontend branches on these rather
    than on human-readable messages. Add codes as the UI needs to distinguish cases."""

    internal_error = "internal_error"
    not_found = "not_found"
    conflict = "conflict"
    validation_error = "validation_error"
    unauthorized = "unauthorized"
    forbidden = "forbidden"


def typed_http_exception(status_code: int, message: str, error_code: ErrorCode) -> HTTPException:
    """Raise API errors through this so they serialize as
    ``{"detail": {"message": ..., "error_code": ...}}``. The frontend fetch wrapper
    flattens ``error_code`` onto ``ApiError.code``."""
    return HTTPException(
        status_code=status_code,
        detail={"message": message, "error_code": error_code.value},
    )
