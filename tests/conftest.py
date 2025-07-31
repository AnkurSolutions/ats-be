# tests/conftest.py
import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = 1
    user.name = "John Doe"
    user.login = "john@example.com"
    user.email = "john@example.com"
    user.exists.return_value = True
    user.groups_id.ids = [10, 20]
    return user


@pytest.fixture
def mock_group_data():
    # Mock ir.model.data search result for groups
    group_record = MagicMock()
    group_record.module = 'base'
    group_record.name = 'group_system'
    return [group_record]

@pytest.fixture
def mock_env(mock_user, mock_group_data):
    env = MagicMock()

    # Existing mocks
    res_users = MagicMock()
    res_users.browse.return_value = mock_user
    res_users.search.return_value = [mock_user]
    res_users.create.return_value = mock_user

    ir_model_data = MagicMock()
    ir_model_data.search.return_value = mock_group_data

    # NEW: Mock ATS models separately
    ats_applicant_profile = MagicMock()
    ats_applicant_profile.search.return_value = MagicMock()
    ats_applicant_profile.create.return_value = MagicMock()

    ats_application = MagicMock()
    ats_application.search.return_value = MagicMock()
    ats_application.create.return_value = MagicMock()

    ats_job = MagicMock()

    # Setup env.__getitem__.side_effect to return the right mocks
    def get_item(name):
        mapping = {
            'res.users': res_users,
            'ir.model.data': ir_model_data,
            'ats.applicant.profile': ats_applicant_profile,
            'ats.application': ats_application,
            'ats.job': ats_job,
        }
        return mapping[name]

    env.__getitem__.side_effect = get_item

    # Mock env.ref for group XML ID lookup
    ref_mock = MagicMock()
    ref_mock.id = 123
    env.ref.return_value = ref_mock

    return env