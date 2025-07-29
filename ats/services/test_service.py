from odoo.api import Environment

def get_test_by_id(env: Environment, test_id: int):
    return env['ats.test'].browse(test_id)

def list_tests(env: Environment, applicant_id=None, status=None, limit=100, offset=0):
    domain = []
    if applicant_id:
        domain.append(('applicant_id', '=', applicant_id))
    if status:
        domain.append(('status', '=', status))

    return env['ats.test'].search(domain, limit=limit, offset=offset)

def create_test(env: Environment, data: dict):
    return env['ats.test'].create(data)

def update_test(env: Environment, test_id: int, data: dict):
    test = get_test_by_id(env, test_id)
    if not test.exists():
        return None
    test.write({k: v for k, v in data.items() if v is not None})
    return test

def delete_test(env: Environment, test_id: int):
    test = get_test_by_id(env, test_id)
    if not test.exists():
        return False
    test.unlink()
    return True
