# ats/services/user_service.py

GROUP_ROLE_MAP = {
    "base.group_system": "admin",
    "hr.group_hr_user": "hr",
    "hr_recruitment.group_hr_recruitment_user": "recruiter",
    # Add your custom group XML ID for interviewer if any
    "ats.group_interviewer": "interviewer"
}

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

def resolve_user_role(env: Environment, user) -> str:
    """
    Resolve user role by checking user's groups' external XML IDs.
    """
    xml_ids = env['ir.model.data'].search([
        ('model', '=', 'res.groups'),
        ('res_id', 'in', user.groups_id.ids)
    ])
    for record in xml_ids:
        if record.module and record.name:
            full_id = f"{record.module}.{record.name}"
            if full_id in GROUP_ROLE_MAP:
                return GROUP_ROLE_MAP[full_id]
    return "user"  # default fallback