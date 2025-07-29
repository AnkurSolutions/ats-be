from odoo.api import Environment

def create_job(env: Environment, data: dict):
    return env['hr.job'].create(data)

def get_job_by_id(env: Environment, job_id: int):
    return env['hr.job'].browse(job_id)

def list_jobs(env: Environment, department_id=None, name=None, limit=100, offset=0):
    domain = []
    if department_id:
        domain.append(('department_id', '=', department_id))
    if name:
        domain.append(('name', 'ilike', name))

    return env['hr.job'].search(domain, limit=limit, offset=offset)

def update_job(env: Environment, job_id: int, data: dict):
    job = get_job_by_id(env, job_id)
    if not job.exists():
        return None
    job.write({k: v for k, v in data.items() if v is not None})
    return job

def delete_job(env: Environment, job_id: int):
    job = get_job_by_id(env, job_id)
    if not job.exists():
        return False
    job.unlink()
    return True
