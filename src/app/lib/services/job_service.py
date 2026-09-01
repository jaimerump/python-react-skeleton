import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select

from app.lib.models.job import Job, JobStatus
from app.lib.schemas.job import JobRecord
from app.lib.services.database import BaseService

_ACTIVE_STATUSES = (JobStatus.NEW, JobStatus.STARTED)


class JobService(BaseService):
    """Manages durable job records (the DB side of async work).

    State machine: NEW -> STARTED -> COMPLETED | FAILED. Transitions lock the row
    with ``SELECT ... FOR UPDATE`` so concurrent workers can't double-process.
    """

    def create_job(self, job_type: str, payload: dict[str, Any] | None = None) -> JobRecord:
        with self._session_context() as session:
            job = Job(job_type=job_type, payload=payload or {}, status=JobStatus.NEW)
            session.add(job)
            session.flush()
            return JobRecord.model_validate(job)

    def has_active_job(self, job_type: str) -> bool:
        """Dedup guard: is there already a NEW/STARTED job of this type?"""
        with self._session_context() as session:
            stmt = select(Job.id).where(
                Job.job_type == job_type, Job.status.in_(_ACTIVE_STATUSES)
            )
            return session.execute(stmt).first() is not None

    def mark_started(self, job_id: uuid.UUID) -> JobRecord:
        return self._transition(job_id, JobStatus.STARTED, started_at=_now())

    def mark_completed(self, job_id: uuid.UUID) -> JobRecord:
        return self._transition(job_id, JobStatus.COMPLETED, finished_at=_now())

    def mark_failed(self, job_id: uuid.UUID, error: str) -> JobRecord:
        return self._transition(job_id, JobStatus.FAILED, finished_at=_now(), error=error)

    def _transition(
        self,
        job_id: uuid.UUID,
        status: JobStatus,
        *,
        started_at: datetime | None = None,
        finished_at: datetime | None = None,
        error: str | None = None,
    ) -> JobRecord:
        with self._session_context() as session:
            job = session.execute(
                select(Job).where(Job.id == job_id).with_for_update()
            ).scalar_one()
            job.status = status
            if started_at is not None:
                job.started_at = started_at
            if finished_at is not None:
                job.finished_at = finished_at
            if error is not None:
                job.error = error
            session.flush()
            return JobRecord.model_validate(job)


def _now() -> datetime:
    return datetime.now(UTC)
