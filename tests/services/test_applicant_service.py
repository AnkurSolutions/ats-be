# tests/services/test_applicant_service.py

import pytest
from unittest.mock import MagicMock
from ats.services.applicant_service import ApplicantService

@pytest.fixture
def mock_env():
    mock_env = MagicMock()
    mock_env['ats.applicant.profile'] = MagicMock()
    mock_env['ats.skill'] = MagicMock()
    return mock_env

@pytest.fixture
def applicant_service(mock_env):
    return ApplicantService(mock_env)

def test_create_profile(applicant_service, mock_env):
    mock_create = MagicMock()
    mock_env['ats.applicant.profile'].create = mock_create

    result = applicant_service.create_profile(
        user_id=1,
        resume_url="https://example.com/resume.pdf",
        skill_ids=[1, 2],
        experience_years=5,
        status='active'
    )

    mock_create.assert_called_once_with({
        'user_id': 1,
        'resume_url': "https://example.com/resume.pdf",
        'skill_ids': [(6, 0, [1, 2])],
        'experience_years': 5,
        'status': 'active'
    })
    assert result == mock_create.return_value

def test_get_profile(applicant_service, mock_env):
    mock_search = MagicMock()
    mock_env['ats.applicant.profile'].search = mock_search

    applicant_service.get_profile(user_id=99)
    mock_search.assert_called_once_with([('user_id', '=', 99)], limit=1)

def test_update_profile(applicant_service, mock_env):
    mock_profile = MagicMock()
    mock_env['ats.applicant.profile'].search.return_value = mock_profile

    result = applicant_service.update_profile(
        user_id=1,
        resume_url="https://cv.com/resume.pdf",
        skill_ids=[1, 2],
        experience_years=3,
        status='inactive'
    )

    mock_profile.write.assert_called_once_with({
        'resume_url': "https://cv.com/resume.pdf",
        'skill_ids': [(6, 0, [1, 2])],
        'experience_years': 3,
        'status': 'inactive',
    })
    assert result == mock_profile

def test_update_profile_not_found(applicant_service, mock_env):
    mock_env['ats.applicant.profile'].search.return_value = None
    with pytest.raises(ValueError, match="Applicant profile does not exist"):
        applicant_service.update_profile(user_id=1)

def test_delete_profile_found(applicant_service, mock_env):
    mock_profile = MagicMock()
    mock_env['ats.applicant.profile'].search.return_value = mock_profile

    result = applicant_service.delete_profile(user_id=42)
    mock_profile.unlink.assert_called_once()
    assert result is True

def test_delete_profile_not_found(applicant_service, mock_env):
    mock_env['ats.applicant.profile'].search.return_value = None
    result = applicant_service.delete_profile(user_id=999)
    assert result is False

def test_list_skills(applicant_service, mock_env):
    applicant_service.list_skills()
    mock_env['ats.skill'].search.assert_called_once_with([])

def test_create_skill_new(applicant_service, mock_env):
    mock_env['ats.skill'].search.return_value = None
    mock_create = MagicMock()
    mock_env['ats.skill'].create = mock_create

    result = applicant_service.create_skill(name="Python")
    mock_create.assert_called_once_with({'name': 'Python'})
    assert result == mock_create.return_value

def test_create_skill_existing(applicant_service, mock_env):
    mock_existing = MagicMock()
    mock_env['ats.skill'].search.return_value = mock_existing

    result = applicant_service.create_skill(name="Python")
    mock_env['ats.skill'].create.assert_not_called()
    assert result == mock_existing
