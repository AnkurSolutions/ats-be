from odoo.api import Environment

class ApplicantService:
    def __init__(self, env: Environment):
        self.env = env
        self.AtsApplicantProfile = env['ats.applicant.profile']
        self.AtsSkill = env['ats.skill']

    def create_profile(self, *, user_id: int, resume_url: str = None, skill_ids: list[int] = None, experience_years: int = 0, status: str = 'active'):
        vals = {
            'user_id': user_id,
            'resume_url': resume_url,
            'experience_years': experience_years,
            'status': status,
        }
        if skill_ids is not None:
            vals['skill_ids'] = [(6, 0, skill_ids)]
        return self.AtsApplicantProfile.create(vals)

    def get_profile(self, user_id: int):
        profile = self.AtsApplicantProfile.search([('user_id', '=', user_id)], limit=1)
        if not profile.exists():
            return None
        return profile

    def update_profile(self, *, user_id: int, resume_url: str = None, skill_ids: list[int] = None, experience_years: int = None, status: str = None):
        profile = self.get_profile(user_id=user_id)
        if not profile:
            raise ValueError("Applicant profile does not exist")
        vals = {}
        if resume_url is not None:
            vals['resume_url'] = resume_url
        if skill_ids is not None:
            vals['skill_ids'] = [(6, 0, skill_ids)]
        if experience_years is not None:
            vals['experience_years'] = experience_years
        if status is not None:
            vals['status'] = status
        profile.write(vals)
        return profile

    def delete_profile(self, *, user_id: int):
        profile = self.get_profile(user_id=user_id)
        if profile:
            profile.unlink()
            return True
        return False

    def list_skills(self):
        return self.AtsSkill.search([])

    def create_skill(self, *, name: str):
        existing = self.AtsSkill.search([('name', '=', name)], limit=1)
        if existing:
            return existing
        return self.AtsSkill.create({'name': name})