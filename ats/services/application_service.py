from odoo.api import Environment

def get_application_by_id(env: Environment, app_id: int):
    return env['hr.applicant'].browse(app_id)

def list_applications(env: Environment, job_id=None, email=None, name=None, user_id=None, limit=100, offset=0):
    domain = []
    if job_id:
        domain.append(('job_id', '=', job_id))
    if email:
        domain.append(('email_from', 'ilike', email))
    if name:
        domain.append(('name', 'ilike', name))
    if user_id:
        domain.append(('user_id', '=', user_id))

    return env['hr.applicant'].search(domain, limit=limit, offset=offset)

def create_application(env: Environment, data: dict):
    values = {
        'name': data['name'],
        'email_from': data.get('email'),
        'job_id': data['job_id'],
        'partner_name': data.get('partner_name'),
        'description': data.get('description'),
        'source_id': data.get('source_id'),
        'user_id': data.get('user_id'),
    }
    return env['hr.applicant'].create(values)

def update_application(env: Environment, app_id: int, data: dict):
    app = get_application_by_id(env, app_id)
    if not app.exists():
        return None
    values = {}
    if 'name' in data: values['name'] = data['name']
    if 'email' in data: values['email_from'] = data['email']
    if 'job_id' in data: values['job_id'] = data['job_id']
    if 'partner_name' in data: values['partner_name'] = data['partner_name']
    if 'description' in data: values['description'] = data['description']
    if 'source_id' in data: values['source_id'] = data['source_id']
    if 'user_id' in data: values['user_id'] = data['user_id']

    app.write(values)
    return app

def delete_application(env: Environment, app_id: int):
    app = get_application_by_id(env, app_id)
    if not app.exists():
        return False
    app.unlink()
    return True

def submit_public_application(env: Environment, job_id: int, data: dict):
    values = {
        'name': data['name'],
        'email_from': data['email'],
        'job_id': job_id,
        'description': f"Resume: {data.get('resume_url')}\n\nCover Letter:\n{data.get('cover_letter') or ''}",
        # Optional: assign to a default stage or user
    }
    return env['hr.applicant'].create(values)