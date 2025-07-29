from odoo.api import Environment

def get_offer_by_id(env: Environment, offer_id: int):
    return env['ats.offer'].browse(offer_id)

def list_offers(env: Environment, applicant_id=None, status=None, limit=100, offset=0):
    domain = []
    if applicant_id:
        domain.append(('applicant_id', '=', applicant_id))
    if status:
        domain.append(('status', '=', status))
    return env['ats.offer'].search(domain, limit=limit, offset=offset)

def create_offer(env: Environment, data: dict):
    return env['ats.offer'].create(data)

def update_offer(env: Environment, offer_id: int, data: dict):
    offer = get_offer_by_id(env, offer_id)
    if not offer.exists():
        return None
    offer.write({k: v for k, v in data.items() if v is not None})
    return offer

def delete_offer(env: Environment, offer_id: int):
    offer = get_offer_by_id(env, offer_id)
    if not offer.exists():
        return False
    offer.unlink()
    return True

def mark_offer_sent(env: Environment, offer_id: int):
    offer = get_offer_by_id(env, offer_id)
    if not offer.exists():
        return None
    offer.action_send()
    return offer

def mark_offer_accepted(env: Environment, offer_id: int):
    offer = get_offer_by_id(env, offer_id)
    if not offer.exists():
        return None
    offer.action_accept()
    return offer

def mark_offer_rejected(env: Environment, offer_id: int):
    offer = get_offer_by_id(env, offer_id)
    if not offer.exists():
        return None
    offer.action_reject()
    return offer
