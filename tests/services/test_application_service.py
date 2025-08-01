import pytest
from unittest.mock import MagicMock
from ats.services.application_service import ApplicationService

@pytest.fixture
def mock_env():
    mock_env = MagicMock()
    mock_env['ats.application'] = MagicMock()
    mock_env['ats.applicant.profile'] = MagicMock()
    mock_env['ats.job'] = MagicMock()
    return mock_env

@pytest.fixture
def application_service(mock_env):
    return ApplicationService(mock_env)

def test_get_profile(application_service, mock_env):
    application_service.get_profile(user_id=42)
    mock_env['ats.applicant.profile'].search.assert_called_once_with([('user_id', '=', 42)], limit=1)

def test_create_application_success(mock_env):
    # Setup mock profile recordset with .exists() and __bool__
    mock_profile = MagicMock()
    mock_profile.id = 123
    mock_profile.exists.return_value = True
    mock_profile.__bool__.return_value = True
    mock_env['ats.applicant.profile'].search.return_value = mock_profile

    # Setup mock existing application recordset with .exists()=False
    mock_existing_app = MagicMock()
    mock_existing_app.exists.return_value = False
    mock_env['ats.application'].search.return_value = mock_existing_app

    # Setup mock application record for create()
    mock_application = MagicMock()
    mock_application.id = 456
    mock_env['ats.application'].create.return_value = mock_application

    service = ApplicationService(mock_env)
    result = service.create_application(user_id=1, job_id=42)

    # Verify calls
    mock_env['ats.applicant.profile'].search.assert_called_once_with([('user_id', '=', 1)], limit=1)
    mock_env['ats.application'].search.assert_called_once_with([('job_id', '=', 42), ('applicant_id', '=', 123)], limit=1)
    mock_env['ats.application'].create.assert_called_once()
    assert result == mock_application

def test_create_application_existing(application_service, mock_env):
    mock_profile = MagicMock()
    mock_profile.id = 10
    mock_profile.exists.return_value = True
    mock_profile.__bool__.return_value = True
    mock_env['ats.applicant.profile'].search.return_value = mock_profile

    mock_existing = MagicMock()
    mock_existing.exists.return_value = True
    mock_env['ats.application'].search.return_value = mock_existing

    result = application_service.create_application(user_id=1, job_id=100)
    assert result == mock_existing
    mock_env['ats.application'].create.assert_not_called()

def test_create_application_no_profile(application_service, mock_env):
    mock_env['ats.applicant.profile'].search.return_value = None
    with pytest.raises(ValueError, match="Applicant profile does not exist"):
        application_service.create_application(user_id=1, job_id=100)

def test_get_applications_with_profile(application_service, mock_env):
    mock_profile = MagicMock()
    mock_profile.id = 10
    mock_profile.exists.return_value = True
    mock_profile.__bool__.return_value = True
    mock_env['ats.applicant.profile'].search.return_value = mock_profile

    mock_applications = MagicMock()
    mock_env['ats.application'].search.return_value = mock_applications

    result = application_service.get_applications(user_id=1)

    mock_env['ats.applicant.profile'].search.assert_called_once_with([('user_id', '=', 1)], limit=1)
    mock_env['ats.application'].search.assert_called_once_with([('applicant_id', '=', 10)])
    assert result == mock_applications

def test_get_applications_no_profile(application_service, mock_env):
    mock_env['ats.applicant.profile'].search.return_value = None

    mock_empty_browse = MagicMock()
    mock_env['ats.application'].browse.return_value = mock_empty_browse

    result = application_service.get_applications(user_id=1)
    mock_env['ats.applicant.profile'].search.assert_called_once_with([('user_id', '=', 1)], limit=1)
    mock_env['ats.application'].browse.assert_called_once()
    assert result == mock_empty_browse

def test_get_application(application_service, mock_env):
    application_service.get_application(application_id=5)
    mock_env['ats.application'].browse.assert_called_once_with(5)

def test_update_application_status_success(application_service, mock_env):
    mock_application = MagicMock()
    mock_application.exists.return_value = True
    mock_env['ats.application'].browse.return_value = mock_application

    result = application_service.update_application_status(application_id=1, status="shortlisted")
    assert result == mock_application
    assert mock_application.status == "shortlisted"

def test_update_application_status_not_exist(application_service, mock_env):
    mock_application = MagicMock()
    mock_application.exists.return_value = False
    mock_env['ats.application'].browse.return_value = mock_application

    with pytest.raises(ValueError, match="Application does not exist"):
        application_service.update_application_status(application_id=1, status="shortlisted")

def test_delete_application_success(application_service, mock_env):
    mock_application = MagicMock()
    mock_application.exists.return_value = True
    mock_env['ats.application'].browse.return_value = mock_application

    result = application_service.delete_application(application_id=1)
    assert result is True
    mock_application.unlink.assert_called_once()

def test_delete_application_not_exist(application_service, mock_env):
    mock_application = MagicMock()
    mock_application.exists.return_value = False
    mock_env['ats.application'].browse.return_value = mock_application

    result = application_service.delete_application(application_id=1)
    assert result is False
    mock_application.unlink.assert_not_called()

def test_search_jobs_no_filters(application_service, mock_env):
    application_service.search_jobs()
    mock_env['ats.job'].search.assert_called_once_with([('status', '=', 'published')])

def test_search_jobs_with_filters(application_service, mock_env):
    application_service.search_jobs(keywords="python", location="NY", job_type="full-time")
    expected_domain = [
        ('status', '=', 'published'),
        '|', ('name', 'ilike', "python"), ('description', 'ilike', "python"),
        ('location', 'ilike', "NY"),
        ('job_type', '=', "full-time")
    ]
    mock_env['ats.job'].search.assert_called_once_with(expected_domain)
