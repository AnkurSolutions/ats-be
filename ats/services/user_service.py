# ats/services/user_service.py

from odoo.api import Environment

def get_user_by_id(env: Environment, user_id: int):
    return env['res.users'].browse(user_id)

def list_users(env: Environment):
    return env['res.users'].search([])

def create_user(env: Environment, data: dict):
    return env['res.users'].create({
        'name': data['name'],
        'login': data['email'],
        'email': data['email'],
        'groups_id': [(6, 0, [resolve_group_id(env, data['role'])])],
        'password': data['password'],
    })

def update_user(env: Environment, user_id: int, data: dict):
    user = get_user_by_id(env, user_id)
    if not user.exists():
        return None
    user.write({k: v for k, v in data.items() if v is not None})
    return user

def delete_user(env: Environment, user_id: int):
    user = get_user_by_id(env, user_id)
    if not user.exists():
        return False
    user.unlink()
    return True

def resolve_group_id(env: Environment, role: str):
    group_map = {
        'admin': 'base.group_system',
        'hr': 'hr.group_hr_user',
        'recruiter': 'hr_recruitment.group_hr_recruitment_user',
        'interviewer': 'hr_recruitment.group_hr_recruitment_interviewer',
    }
    return get_group_id_from_xml(env, group_map[role])

def get_group_id_from_xml(env: Environment, xml_id: str):
    return env.ref(xml_id).id
