from odoo.api import Environment


class ApplicantService:
    def __init__(self, env: Environment):
        self.env = env
        self.AtsApplicantProfile = env['ats.applicant.profile']
        self.AtsSkill = env['ats.skill']

    def onboard_applicant(
        self,
        *,
        user,
        resume_url: str = None,
        skill_ids: list[int] = None,
        experience_years: int = 0,
        status: str = 'active'
    ):
        try:
            vals = {
                'user_id': user.id,
                'resume_url': resume_url,
                'experience_years': experience_years,
                'status': status,
            }

            if skill_ids is not None:
                if not isinstance(skill_ids, list):
                    raise ValueError("skill_ids must be a list of integers.")
                vals['skill_ids'] = [(6, 0, skill_ids)]

            return self.AtsApplicantProfile.create(vals)

        except Exception as e:
            raise ValueError(f"Failed to onboard applicant: {str(e)}")

    def get_profile(self, user_id: int):
        try:
            profile = self.AtsApplicantProfile.search([('user_id', '=', user_id)], limit=1)
            return profile if profile.exists() else None
        except Exception as e:
            raise ValueError(f"Failed to fetch applicant profile: {str(e)}")

    def update_profile(
        self,
        *,
        user_id: int,
        resume_url: str = None,
        skill_ids: list[int] = None,
        experience_years: int = None,
        status: str = None
    ):
        profile = self.get_profile(user_id=user_id)
        if not profile:
            raise ValueError("Applicant profile does not exist for this user.")

        try:
            vals = {}
            if resume_url is not None:
                vals['resume_url'] = resume_url
            if skill_ids is not None:
                if not isinstance(skill_ids, list):
                    raise ValueError("skill_ids must be a list of integers.")
                vals['skill_ids'] = [(6, 0, skill_ids)]
            if experience_years is not None:
                vals['experience_years'] = experience_years
            if status is not None:
                vals['status'] = status

            profile.write(vals)
            return profile

        except Exception as e:
            raise ValueError(f"Failed to update applicant profile: {str(e)}")

    def delete_profile(self, *, user_id: int):
        profile = self.get_profile(user_id=user_id)
        if not profile:
            return False

        try:
            profile.unlink()
            return True
        except Exception as e:
            raise ValueError(f"Failed to delete profile: {str(e)}")

    def list_skills(self):
        try:
            return self.AtsSkill.search([])
        except Exception as e:
            raise ValueError(f"Failed to fetch skills: {str(e)}")

    def create_skill(self, *, name: str):
        if not name.strip():
            raise ValueError("Skill name must not be empty.")

        try:
            existing = self.AtsSkill.search([('name', '=', name)], limit=1)
            return existing if existing else self.AtsSkill.create({'name': name})
        except Exception as e:
            raise ValueError(f"Failed to create skill: {str(e)}")