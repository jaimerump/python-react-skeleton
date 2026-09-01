"""Authentication/authorization dependencies.

Auth is a SEPARATE ``Depends(...)`` concern from service resolution -- never fold it
into the DI container. Endpoints that need an authorized entity declare it explicitly:

    @router.get("/me")
    async def me(principal: Principal = Depends(require_principal)):
        ...

This is a stub returning an anonymous principal; replace ``require_principal`` with a
real token/session check when auth is added.
"""

from dataclasses import dataclass

from fastapi import Request

from app.api.schemas.base import ErrorCode, typed_http_exception


@dataclass(frozen=True)
class Principal:
    """The authenticated caller. Extend with roles/permissions as needed."""

    id: str
    is_authenticated: bool


def require_principal(request: Request) -> Principal:
    """Placeholder that rejects everything until real auth is wired in.

    Kept intentionally strict so an unprotected endpoint fails closed rather than
    silently allowing anonymous access.
    """
    raise typed_http_exception(
        status_code=401,
        message="Authentication is not configured.",
        error_code=ErrorCode.unauthorized,
    )
