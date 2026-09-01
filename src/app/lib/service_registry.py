"""Central DI registration. Uses CORE ``svcs`` only (never ``svcs.fastapi``) so both
the API and the worker reuse it.

Each service = a class extending ``BaseService`` + a ``create_*`` factory + one
registration line. Group registrations into ``register_<domain>_services`` functions
so a future separate app can register just its slice. DI is lazy, so registering the
full set in every process is harmless.
"""

import svcs

from app.lib.services.database import DatabaseService
from app.lib.services.job_service import JobService
from app.lib.sqs import SQSClient


def create_job_service(services: svcs.Container) -> JobService:
    return JobService(services.get(DatabaseService))


def register_core_services(registry: svcs.Registry) -> None:
    # Singletons with cleanup hooks.
    database_service = DatabaseService()
    registry.register_value(
        DatabaseService, database_service, on_registry_close=database_service.close
    )
    registry.register_value(SQSClient, SQSClient())

    # Lazily-built, per-container services.
    registry.register_factory(JobService, create_job_service)


def register_all_services(registry: svcs.Registry) -> None:
    register_core_services(registry)
    # register_<domain>_services(registry)  # add per-domain groups here
