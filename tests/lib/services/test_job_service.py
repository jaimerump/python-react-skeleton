from app.lib.models.job import JobStatus
from app.lib.services.database import DatabaseService
from app.lib.services.job_service import JobService


def test_create_job_starts_new_and_active(database_service: DatabaseService) -> None:
    service = JobService(database_service)
    record = service.create_job("my_job", {"x": 1})

    assert record.status == JobStatus.NEW
    assert record.payload == {"x": 1}
    assert service.has_active_job("my_job") is True


def test_full_lifecycle_clears_active(database_service: DatabaseService) -> None:
    service = JobService(database_service)
    record = service.create_job("my_job")

    started = service.mark_started(record.id)
    assert started.status == JobStatus.STARTED
    assert started.started_at is not None

    completed = service.mark_completed(record.id)
    assert completed.status == JobStatus.COMPLETED
    assert completed.finished_at is not None
    assert service.has_active_job("my_job") is False


def test_mark_failed_records_error(database_service: DatabaseService) -> None:
    service = JobService(database_service)
    record = service.create_job("my_job")

    failed = service.mark_failed(record.id, "boom")
    assert failed.status == JobStatus.FAILED
    assert failed.error == "boom"
    assert service.has_active_job("my_job") is False
