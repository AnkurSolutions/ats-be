import pytest
from unittest.mock import MagicMock
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
from ats.services.job_service import JobService
from ats.models.job import JobStatus, ApprovalStatus


@pytest.fixture
def fake_env():
    env = MagicMock()
    ats_job = MagicMock()
    ats_job_approval = MagicMock()

    env.__getitem__.side_effect = lambda model_name: {
        'ats.job': ats_job,
        'ats.job.approval': ats_job_approval,
    }[model_name]

    return env, ats_job, ats_job_approval


@pytest.fixture
def job_service(fake_env):
    env, ats_job, ats_job_approval = fake_env
    return JobService(env)


def test_create_job(fake_env, job_service):
    env, ats_job, _ = fake_env
    ats_job.create.return_value = MagicMock(id=1, name="Test Job", status=JobStatus.DRAFT.value)

    job = job_service.create_job(title="Test Job", description="<p>desc</p>", created_by_id=42)

    ats_job.create.assert_called_once()
    assert job.name == "Test Job.name"
    assert job.status == JobStatus.DRAFT.value


def test_update_job_success(fake_env, job_service):
    env, ats_job, _ = fake_env
    job = MagicMock()
    job.exists.return_value = True
    job.status = JobStatus.DRAFT.value
    ats_job.browse.return_value = job

    updated_job = job_service.update_job(job_id=1, updater_id=42, title="New Title", description="New Desc")

    assert job.name == "New Title"
    assert job.description == "New Desc"
    job.write.assert_called_once()
    assert updated_job == job


def test_update_job_fails_if_status_published(fake_env, job_service):
    env, ats_job, _ = fake_env
    job = MagicMock()
    job.exists.return_value = True
    job.status = JobStatus.PUBLISHED.value
    ats_job.browse.return_value = job

    with pytest.raises(ValidationError):
        job_service.update_job(job_id=1, updater_id=42, title="New Title")


def test_approve_job_approve_success(fake_env, job_service):
    env, ats_job, ats_job_approval = fake_env
    job = MagicMock()
    job.exists.return_value = True
    job.status = JobStatus.DRAFT.value
    ats_job.browse.return_value = job
    ats_job_approval.create.return_value = MagicMock(id=123)

    updated_job, approval = job_service.approve_job(job_id=1, approver_id=42, approve=True, comment="Looks good")

    ats_job_approval.create.assert_called_once()
    assert updated_job.status == JobStatus.APPROVED.value
    assert approval.id == 123


def test_approve_job_reject_success(fake_env, job_service):
    env, ats_job, ats_job_approval = fake_env
    job = MagicMock()
    job.exists.return_value = True
    job.status = JobStatus.DRAFT.value
    ats_job.browse.return_value = job
    ats_job_approval.create.return_value = MagicMock(id=456)

    updated_job, approval = job_service.approve_job(job_id=1, approver_id=42, approve=False, comment="Needs update")

    ats_job_approval.create.assert_called_once()
    assert updated_job.status == JobStatus.DRAFT.value
    assert approval.id == 456


def test_approve_job_fails_if_not_draft_and_approving(fake_env, job_service):
    env, ats_job, _ = fake_env
    job = MagicMock()
    job.exists.return_value = True
    job.status = JobStatus.PUBLISHED.value
    ats_job.browse.return_value = job

    with pytest.raises(ValidationError):
        job_service.approve_job(job_id=1, approver_id=42, approve=True)


def test_publish_job_success(fake_env, job_service):
    env, ats_job, _ = fake_env
    job = MagicMock()
    job.exists.return_value = True
    job.status = JobStatus.APPROVED.value
    ats_job.browse.return_value = job

    updated_job = job_service.publish_job(job_id=1, publisher_id=42)

    assert updated_job.status == JobStatus.PUBLISHED.value


def test_publish_job_fails_if_not_approved(fake_env, job_service):
    env, ats_job, _ = fake_env
    job = MagicMock()
    job.exists.return_value = True
    job.status = JobStatus.DRAFT.value
    ats_job.browse.return_value = job

    with pytest.raises(ValidationError):
        job_service.publish_job(job_id=1, publisher_id=42)


def test_close_job_success_from_published(fake_env, job_service):
    env, ats_job, _ = fake_env
    job = MagicMock()
    job.exists.return_value = True
    job.status = JobStatus.PUBLISHED.value
    ats_job.browse.return_value = job

    updated_job = job_service.close_job(job_id=1, closer_id=42)

    assert updated_job.status == JobStatus.CLOSED.value


def test_close_job_success_from_closed(fake_env, job_service):
    env, ats_job, _ = fake_env
    job = MagicMock()
    job.exists.return_value = True
    job.status = JobStatus.CLOSED.value
    ats_job.browse.return_value = job

    updated_job = job_service.close_job(job_id=1, closer_id=42)

    assert updated_job.status == JobStatus.CLOSED.value


def test_close_job_fails_if_invalid_status(fake_env, job_service):
    env, ats_job, _ = fake_env
    job = MagicMock()
    job.exists.return_value = True
    job.status = JobStatus.DRAFT.value
    ats_job.browse.return_value = job

    with pytest.raises(ValidationError):
        job_service.close_job(job_id=1, closer_id=42)


def test_reopen_job_success(fake_env, job_service):
    env, ats_job, _ = fake_env
    job = MagicMock()
    job.exists.return_value = True
    job.status = JobStatus.CLOSED.value
    ats_job.browse.return_value = job

    updated_job = job_service.reopen_job(job_id=1, reopener_id=42)

    assert updated_job.status == JobStatus.PUBLISHED.value


def test_reopen_job_fails_if_not_closed(fake_env, job_service):
    env, ats_job, _ = fake_env
    job = MagicMock()
    job.exists.return_value = True
    job.status = JobStatus.PUBLISHED.value
    ats_job.browse.return_value = job

    with pytest.raises(ValidationError):
        job_service.reopen_job(job_id=1, reopener_id=42)


def test_auto_archive_jobs(fake_env, job_service):
    env, ats_job, _ = fake_env
    old_date = datetime.now() - timedelta(days=100)
    job1 = MagicMock(status=JobStatus.DRAFT.value, last_status_update_at=old_date)
    job2 = MagicMock(status=JobStatus.PUBLISHED.value, last_status_update_at=old_date)
    ats_job.search.return_value = [job1, job2]

    archived_jobs = job_service.auto_archive_jobs()

    for job in [job1, job2]:
        assert job.status == JobStatus.ARCHIVED.value


def test_get_job_success(fake_env, job_service):
    env, ats_job, _ = fake_env
    job = MagicMock()
    job.exists.return_value = True
    ats_job.browse.return_value = job

    result = job_service.get_job(job_id=1)

    assert result == job


def test_get_job_not_found(fake_env, job_service):
    env, ats_job, _ = fake_env
    job = MagicMock()
    job.exists.return_value = False
    ats_job.browse.return_value = job

    with pytest.raises(ValidationError):
        job_service.get_job(job_id=1)


def test_list_jobs_no_filters(fake_env, job_service):
    env, ats_job, _ = fake_env
    ats_job.search.return_value = [MagicMock(id=1), MagicMock(id=2)]

    results = job_service.list_jobs()

    ats_job.search.assert_called_once()
    assert len(results) == 2


def test_list_jobs_with_filters(fake_env, job_service):
    env, ats_job, _ = fake_env
    ats_job.search.return_value = [MagicMock(id=1)]

    results = job_service.list_jobs(filters={"status": JobStatus.PUBLISHED.value})

    ats_job.search.assert_called_once_with(
        [('status', '=', JobStatus.PUBLISHED.value)], limit=50, offset=0, order='create_date desc'
    )
    assert len(results) == 1
