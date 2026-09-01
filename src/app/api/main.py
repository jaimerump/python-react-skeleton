import asyncio
import logging
from collections.abc import AsyncGenerator

import svcs
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm.exc import StaleDataError

from app.api.middleware import (
    CorrelationIdMiddleware,
    CsrfMiddleware,
    SecurityHeadersMiddleware,
)
from app.api.router_registry import mount_all_routers
from app.api.schemas.base import ErrorCode
from app.lib.service_registry import register_all_services
from app.lib.services.database import DatabaseService, wait_for_database_schema

logger = logging.getLogger(__name__)


@svcs.fastapi.lifespan
async def lifespan(
    app: FastAPI, registry: svcs.Registry
) -> AsyncGenerator[dict[str, object] | None, None]:
    # Services depend on a live, migrated DB -- block on schema readiness first.
    # Build the DB service once here for the readiness probe; register_all_services
    # registers its own singleton for request handling.
    database_service = DatabaseService()
    try:
        await asyncio.get_running_loop().run_in_executor(
            None, wait_for_database_schema, database_service
        )
    finally:
        database_service.close()
    register_all_services(registry)
    yield None


def create_app() -> FastAPI:
    app = FastAPI(title="app API", lifespan=lifespan)

    mount_all_routers(app)
    _register_exception_handlers(app)

    # Middleware runs last-added-first, so add in reverse of desired execution order.
    # Desired order: CORS -> CorrelationId -> CSRF -> SecurityHeaders.
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(CsrfMiddleware)
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # tighten per environment
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


def _register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(StaleDataError)
    async def _handle_stale_data(request: Request, exc: StaleDataError) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={
                "detail": {
                    "message": "The resource was modified concurrently. Retry.",
                    "error_code": ErrorCode.conflict.value,
                }
            },
        )

    @app.exception_handler(Exception)
    async def _handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
        # Let FastAPI/Starlette handle its own HTTPExceptions normally.
        if isinstance(exc, HTTPException):
            raise exc
        logger.exception("Unhandled exception")
        return JSONResponse(
            status_code=500,
            content={
                "detail": {
                    "message": "Internal server error.",
                    "error_code": ErrorCode.internal_error.value,
                }
            },
        )


app = create_app()
