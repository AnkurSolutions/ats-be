# tests/services/test_user_service.py
from unittest.mock import MagicMock
import pytest
from ats.services import user_service


def test_get_user_by_id(mock_env, mock_user):
    user = user_service.get_user_by_id(mock_env, 42)
    mock_env['res.users'].browse.assert_called_once_with(42)
    assert user == mock_user


def test_list_users(mock_env, mock_user):
    users = user_service.list_users(mock_env)
    mock_env['res.users'].search.assert_called_once_with([])
    assert users == [mock_user]


def test_create_user(mock_env):
    data = {
        'name': 'Alice Smith',
        'email': 'alice@example.com',
        'role': 'admin',
        'password': 'password123'
    }

    created = user_service.create_user(mock_env, data)
    mock_env['res.users'].create.assert_called_once()
    create_args = mock_env['res.users'].create.call_args[0][0]

    assert create_args['name'] == data['name']
    assert create_args['login'] == data['email']
    assert create_args['email'] == data['email']
    assert create_args['password'] == data['password']
    assert create_args['groups_id'] == [(6, 0, [123])]
    assert created == mock_env['res.users'].create.return_value


def test_update_user_success(mock_env, mock_user):
    data = {'name': 'New Name', 'login': 'new.login@example.com'}
    result = user_service.update_user(mock_env, user_id=1, data=data)

    mock_user.write.assert_called_once_with(data)
    assert result == mock_user


def test_update_user_not_exists(mock_env, mock_user):
    mock_user.exists.return_value = False
    result = user_service.update_user(mock_env, user_id=1, data={'name': 'X'})
    assert result is None
    mock_user.write.assert_not_called()


def test_delete_user_success(mock_env, mock_user):
    result = user_service.delete_user(mock_env, user_id=1)
    mock_user.unlink.assert_called_once()
    assert result is True


def test_delete_user_not_exists(mock_env, mock_user):
    mock_user.exists.return_value = False
    result = user_service.delete_user(mock_env, user_id=1)
    assert result is False
    mock_user.unlink.assert_not_called()


def test_resolve_group_id(mock_env):
    group_id = user_service.resolve_group_id(mock_env, role="admin")
    mock_env.ref.assert_called_once_with("base.group_system")
    assert group_id == 123


def test_get_group_id_from_xml(mock_env):
    group_id = user_service.get_group_id_from_xml(mock_env, "base.group_hr_user")
    mock_env.ref.assert_called_once_with("base.group_hr_user")
    assert group_id == 123


def test_resolve_user_role_admin(mock_env, mock_user):
    role = user_service.resolve_user_role(mock_env, mock_user)
    mock_env['ir.model.data'].search.assert_called_once_with([
        ('model', '=', 'res.groups'),
        ('res_id', 'in', mock_user.groups_id.ids)
    ])
    assert role == "admin"


def test_resolve_user_role_default(mock_env, mock_user):
    # Override mock to return group not in GROUP_ROLE_MAP
    fake_group = MagicMock(module='foo', name='bar')
    mock_env['ir.model.data'].search.return_value = [fake_group]

    role = user_service.resolve_user_role(mock_env, mock_user)
    assert role == "user"