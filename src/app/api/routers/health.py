import svcs
from fastapi import APIRouter

from app.api.schemas.base import ErrorCode, ResponseSchema, typed_http_exception
from app.lib.services.database import DatabaseService

router = APIRouter(tags=["health"])


class HealthResponse(ResponseSchema):
    status: str


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Liveness: the process is up. Does not touch dependencies."""
    return HealthResponse(status="ok")


@router.get("/ready", response_model=HealthResponse)
async def ready(services: svcs.fastapi.DepContainer) -> HealthResponse:
    """Readiness: dependencies (the database) are reachable."""
    database_service = await services.aget(DatabaseService)
    if not database_service.check_health():
        raise typed_http_exception(
            status_code=503,
            message="Database is not reachable.",
            error_code=ErrorCode.internal_error,
        )
    return HealthResponse(status="ok")
