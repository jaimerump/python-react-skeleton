"""Handler registry surface.

⚠ THE #1 SILENT TRAP: ``@register_handler`` only runs on import. Every new handler
module MUST be imported at the BOTTOM of this file, or every message of that type
raises ``UnknownJobTypeError`` and goes straight to the DLQ.
"""

from app.worker.handlers.base import (
    JobHandler,
    get_handler,
    register_handler,
    registered_job_types,
)
from app.worker.handlers.services import WorkerServices

__all__ = [
    "JobHandler",
    "WorkerServices",
    "get_handler",
    "register_handler",
    "registered_job_types",
]

# --- Import handler modules below to trigger their @register_handler registration ---
# from app.worker.handlers import promote_to_public  # noqa: E402,F401
