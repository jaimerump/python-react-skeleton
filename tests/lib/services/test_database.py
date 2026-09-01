from sqlalchemy import select

from app.lib.models.job import Job
from app.lib.services.database import DatabaseService


def test_check_health_returns_true(database_service: DatabaseService) -> None:
    assert database_service.check_health() is True


def test_session_scope_commits_on_success(database_service: DatabaseService) -> None:
    with database_service.session_scope() as session:
        session.add(Job(job_type="t", payload={}))

    with database_service.session_scope() as session:
        assert session.execute(select(Job)).scalars().all()


def test_session_scope_rolls_back_on_error(database_service: DatabaseService) -> None:
    try:
        with database_service.session_scope() as session:
            session.add(Job(job_type="t", payload={}))
            raise RuntimeError("boom")
    except RuntimeError:
        pass

    with database_service.session_scope() as session:
        assert session.execute(select(Job)).scalars().all() == []
