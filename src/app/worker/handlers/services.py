"""Service wiring for handlers. The worker builds its OWN svcs container from the
shared ``lib/service_registry.py`` -- there is no FastAPI in this process."""

from dataclasses import dataclass

import svcs

from app.lib.service_registry import register_all_services
from app.lib.services.job_service import JobService


@dataclass
class WorkerServices:
    """The services a handler needs, resolved from the shared registry. Extend this
    as handlers require more services."""

    job_service: JobService

    @classmethod
    async def create(cls) -> "WorkerServices":
        registry = svcs.Registry()
        register_all_services(registry)
        async with svcs.Container(registry) as container:
            return cls(job_service=await container.aget(JobService))
