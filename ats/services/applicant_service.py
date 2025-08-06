from odoo.api import Environment


class ApplicantService:
    def __init__(self, env: Environment):
        self.env = env
        self.AtsApplicantProfile = env['ats.applicant.profile']
        self.AtsSkill = env['ats.skill']
        self.AtsApplicationTag = env['ats.application.tag']

    def onboard_applicant(self, *, user, **data):
        try:
            vals = {
                'user_id': user["id"],
                'resume_url': data.get('resume_url'),
                'phone': data.get('phone'),
                'email': data.get('email'),
                'experience_years': data.get('experience_years', 0),
                'education_summary': data.get('education_summary'),
                'work_summary': data.get('work_summary'),
                'preferred_job_types': data.get('preferred_job_types'),
                'current_location': data.get('current_location'),
                'parse_metadata': data.get('parse_metadata') or {},
                'status': data.get('status', 'active'),
                'stage': data.get('stage', 'shortlisted'),
            }

            if skill_ids := data.get('skill_ids'):
                if not isinstance(skill_ids, list):
                    raise ValueError("skill_ids must be a list of integers.")
                vals['skill_ids'] = [(6, 0, skill_ids)]

            if tag_ids := data.get('tag_ids'):
                if not isinstance(tag_ids, list):
                    raise ValueError("tag_ids must be a list of integers.")
                vals['tag_ids'] = [(6, 0, tag_ids)]

            return self.AtsApplicantProfile.create(vals)

        except Exception as e:
            raise ValueError(f"Failed to onboard applicant: {str(e)}")

    def get_profile(self, user_id: int):
        try:
            profile = self.AtsApplicantProfile.search([('user_id', '=', user_id)], limit=1)
            return profile if profile.exists() else None
        except Exception as e:
            raise ValueError(f"Failed to fetch applicant profile: {str(e)}")

    def update_profile(self, *, user_id: int, **data):
        profile = self.get_profile(user_id=user_id)
        if not profile:
            raise ValueError("Applicant profile does not exist for this user.")

        try:
            vals = {}

            for field in [
                'resume_url', 'phone', 'email', 'experience_years',
                'education_summary', 'work_summary',
                'preferred_job_types', 'current_location',
                'parse_metadata', 'status', 'stage'
            ]:
                if field in data and data[field] is not None:
                    vals[field] = data[field]

            if 'skill_ids' in data and data['skill_ids'] is not None:
                if not isinstance(data['skill_ids'], list):
                    raise ValueError("skill_ids must be a list of integers.")
                vals['skill_ids'] = [(6, 0, data['skill_ids'])]

            if 'tag_ids' in data and data['tag_ids'] is not None:
                if not isinstance(data['tag_ids'], list):
                    raise ValueError("tag_ids must be a list of integers.")
                vals['tag_ids'] = [(6, 0, data['tag_ids'])]

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

    def list_tags(self):
        try:
            return self.AtsApplicationTag.search([])
        except Exception as e:
            raise ValueError(f"Failed to fetch tags: {str(e)}")

    def create_tag(self, *, name: str, auto_generated: bool = False):
        if not name.strip():
            raise ValueError("Tag name must not be empty.")

        try:
            existing = self.AtsApplicationTag.search([('name', '=', name)], limit=1)
            return existing if existing else self.AtsApplicationTag.create({
                'name': name,
                'auto_generated': auto_generated
            })
        except Exception as e:
            raise ValueError(f"Failed to create tag: {str(e)}")