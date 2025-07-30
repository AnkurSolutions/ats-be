import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import status

from ats.api.v1 import job_router
from ats.main import app  # assuming you mount job_router in your FastAPI app as `/api/v1/jobs`

# Mount router for testing if not done already:
app.include_router(job_router.router, prefix="/api/v1/jobs")


# Helper to override dependencies
def override_get_current_user(role="recruiter", user_id=1):
    async def _override():
        return {"id": user_id, "name": "Test User", "email": "test@example.com", "role": role}
    return _override


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_job_service():
    with patch("api.v1.job_router.JobService", autospec=True) as mock_service_cls:
        mock_service = mock_service_cls.return_value
        yield mock_service


@pytest.mark.parametrize("role,expected_status", [
    ("recruiter", 201),
    ("admin", 201),
    ("hr", 403),  # HR should NOT create jobs
])
def test_create_job_role_based(client, mock_job_service, role, expected_status):
    app.dependency_overrides[job_router.get_current_user] = override_get_current_user(role=role)
    app.dependency_overrides[job_router.get_job_service] = lambda: mock_job_service

    mock_job_service.create_job = AsyncMock(return_value=MagicMock(id=1, name="Job 1", description="<p></p>", status="draft", created_by={"id":1}, last_status_update_at=None))

    response = client.post("/api/v1/jobs/", json={"title": "Job 1", "description": "<p>desc</p>"})

    assert response.status_code == expected_status
    if expected_status == 201:
        assert response.json()["name"] == "Job 1"

    app.dependency_overrides.clear()


def test_get_job_success(client, mock_job_service):
    app.dependency_overrides[job_router.get_current_user] = override_get_current_user(role="recruiter")
    app.dependency_overrides[job_router.get_job_service] = lambda: mock_job_service

    mock_job_service.get_job = AsyncMock(return_value=MagicMock(id=1, name="Job 1", description="<p></p>", status="draft", created_by={"id":1}, last_status_update_at=None))

    response = client.get("/api/v1/jobs/1")

    assert response.status_code == 200
    app.dependency_overrides.clear()


@pytest.mark.parametrize("role,expected_status", [
    ("recruiter", 200),
    ("admin", 200),
    ("hr", 403),  # HR cannot update jobs
])
def test_update_job_role_based(client, mock_job_service, role, expected_status):
    app.dependency_overrides[job_router.get_current_user] = override_get_current_user(role=role)
    app.dependency_overrides[job_router.get_job_service] = lambda: mock_job_service

    mock_job_service.update_job = AsyncMock(return_value=MagicMock(id=1, name="Updated Job", description="Updated", status="draft", created_by={"id":1}, last_status_update_at=None))

    response = client.put("/api/v1/jobs/1", json={"title": "Updated Job", "description": "Updated"})

    assert response.status_code == expected_status
    app.dependency_overrides.clear()


@pytest.mark.parametrize("role,expected_status", [
    ("hr", 200),
    ("recruiter", 403),
    ("admin", 403),
])
def test_approve_job_role_based(client, mock_job_service, role, expected_status):
    app.dependency_overrides[job_router.get_current_user] = override_get_current_user(role=role)
    app.dependency_overrides[job_router.get_job_service] = lambda: mock_job_service

    mock_job_service.approve_job = AsyncMock(return_value=(MagicMock(id=1), MagicMock(id=1)))

    response = client.post("/api/v1/jobs/1/approve", json={"status": "approved", "comment": "Looks good"})

    assert response.status_code == expected_status
    app.dependency_overrides.clear()


@pytest.mark.parametrize("role,expected_status", [
    ("admin", 200),
    ("recruiter", 403),
    ("hr", 403),
])
def test_publish_job_role_based(client, mock_job_service, role, expected_status):
    app.dependency_overrides[job_router.get_current_user] = override_get_current_user(role=role)
    app.dependency_overrides[job_router.get_job_service] = lambda: mock_job_service

    mock_job_service.publish_job = AsyncMock(return_value=MagicMock(id=1))

    response = client.post("/api/v1/jobs/1/publish")

    assert response.status_code == expected_status
    app.dependency_overrides.clear()


@pytest.mark.parametrize("role,expected_status", [
    ("hr", 200),
    ("admin", 200),
    ("recruiter", 403),
])
def test_close_job_role_based(client, mock_job_service, role, expected_status):
    app.dependency_overrides[job_router.get_current_user] = override_get_current_user(role=role)
    app.dependency_overrides[job_router.get_job_service] = lambda: mock_job_service

    mock_job_service.close_job = AsyncMock(return_value=MagicMock(id=1))

    response = client.post("/api/v1/jobs/1/close")

    assert response.status_code == expected_status
    app.dependency_overrides.clear()


@pytest.mark.parametrize("role,expected_status", [
    ("hr", 200),
    ("admin", 200),
    ("recruiter", 403),
])
def test_reopen_job_role_based(client, mock_job_service, role, expected_status):
    app.dependency_overrides[job_router.get_current_user] = override_get_current_user(role=role)
    app.dependency_overrides[job_router.get_job_service] = lambda: mock_job_service

    mock_job_service.reopen_job = AsyncMock(return_value=MagicMock(id=1))

    response = client.post("/api/v1/jobs/1/reopen")

    assert response.status_code == expected_status
    app.dependency_overrides.clear()


def test_list_jobs(client, mock_job_service):
    app.dependency_overrides[job_router.get_current_user] = override_get_current_user(role="recruiter")
    app.dependency_overrides[job_router.get_job_service] = lambda: mock_job_service

    mock_job_service.list_jobs = AsyncMock(return_value=[
        MagicMock(id=1, name="Job 1", description="", status="draft", created_by={"id":1}, last_status_update_at=None),
        MagicMock(id=2, name="Job 2", description="", status="published", created_by={"id":2}, last_status_update_at=None),
    ])

    response = client.get("/api/v1/jobs/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2

    app.dependency_overrides.clear()
