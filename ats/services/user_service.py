# ats/services/user_service.py

GROUP_ROLE_MAP = {
    "base.group_system": "admin",
    "hr.group_hr_user": "hr",
    "hr_recruitment.group_hr_recruitment_user": "recruiter",
    "ats.group_interviewer": "interviewer",
    "base.group_user": "applicant",
}

from odoo.api import Environment

def get_user_by_id(env: Environment, user_id: int):
    return env['res.users'].browse(user_id)

def list_users(env: Environment):
    return env['res.users'].search([])

def create_user(env: Environment, data: dict):
    user_vals = {
        'name': data['name'],
        'login': data['email'],
        'email': data['email'],
        'groups_id': [(6, 0, [resolve_group_id(env, data['role'])])],
        'password': data['password'],
    }
    
    # Set is_applicant flag for applicants
    if data['role'] == 'applicant':
        user_vals['is_applicant'] = True
        
    user = env['res.users'].create(user_vals)
    
    # Create applicant profile if it's an applicant
    if data['role'] == 'applicant':
        env['ats.applicant.profile'].create({
            'user_id': user.id,
            'experience_years': 0,
            'status': 'active',
        })
    
    return user

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
        'applicant': 'base.group_user',
    }
    return get_group_id_from_xml(env, group_map[role])

def get_group_id_from_xml(env: Environment, xml_id: str):
    return env.ref(xml_id).id

def resolve_user_role(env: Environment, user) -> str:
    """
    Resolve user role by checking user's groups' external XML IDs.
    """
    if getattr(user, 'is_applicant', False):
        return "applicant"
    # existing logic:
    xml_ids = env['ir.model.data'].search([
        ('model', '=', 'res.groups'),
        ('res_id', 'in', user.groups_id.ids)
    ])
    for record in xml_ids:
        if record.module and record.name:
            full_id = f"{record.module}.{record.name}"
            if full_id in GROUP_ROLE_MAP:
                return GROUP_ROLE_MAP[full_id]
    return "user"