import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.lib.models.job import JobStatus


class JobRecord(BaseModel):
    """Framework-agnostic view of a job row, used by services and handlers."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_type: str
    status: JobStatus
    payload: dict[str, Any]
    error: str | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
