from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})
_HEADER_NAME = "X-CSRF-Token"
_COOKIE_NAME = "csrftoken"


class CsrfMiddleware(BaseHTTPMiddleware):
    """Double-submit-cookie CSRF check for state-changing requests.

    Requires that the ``X-CSRF-Token`` header matches the ``csrftoken`` cookie on
    unsafe methods. Cookie-less clients (e.g. bearer-token APIs) are unaffected: if no
    CSRF cookie is present, the check is skipped. Wire up token issuance to your auth
    flow as needed.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method not in _SAFE_METHODS:
            cookie_token = request.cookies.get(_COOKIE_NAME)
            if cookie_token is not None:
                header_token = request.headers.get(_HEADER_NAME)
                if not header_token or header_token != cookie_token:
                    return JSONResponse(
                        status_code=403,
                        content={
                            "detail": {
                                "message": "CSRF token missing or invalid.",
                                "error_code": "forbidden",
                            }
                        },
                    )
        return await call_next(request)
