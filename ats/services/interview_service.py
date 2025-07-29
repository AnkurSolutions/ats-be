from odoo.api import Environment

def get_interview_by_id(env: Environment, interview_id: int):
    return env['ats.interview'].browse(interview_id)

def list_interviews(env: Environment, applicant_id=None, interviewer_id=None, status=None, limit=100, offset=0):
    domain = []
    if applicant_id:
        domain.append(('applicant_id', '=', applicant_id))
    if interviewer_id:
        domain.append(('interviewer_id', '=', interviewer_id))
    if status:
        domain.append(('status', '=', status))

    return env['ats.interview'].search(domain, limit=limit, offset=offset)

def create_interview(env: Environment, data: dict):
    return env['ats.interview'].create(data)

def update_interview(env: Environment, interview_id: int, data: dict):
    interview = get_interview_by_id(env, interview_id)
    if not interview.exists():
        return None
    interview.write({k: v for k, v in data.items() if v is not None})
    return interview

def delete_interview(env: Environment, interview_id: int):
    interview = get_interview_by_id(env, interview_id)
    if not interview.exists():
        return False
    interview.unlink()
    return True