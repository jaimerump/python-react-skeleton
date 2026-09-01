"""Central router mounting. Keeps ``main.py`` thin.

⚠ Route-match order: register static paths (e.g. ``/members/bulk``) before dynamic
ones (``/{member_id}``) when a domain has both.
"""

from fastapi import FastAPI

from app.api.routers import health


def mount_all_routers(app: FastAPI) -> None:
    app.include_router(health.router)
    # app.include_router(<domain>.router, prefix="/<domain>")
