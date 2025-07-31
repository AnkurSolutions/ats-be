from datetime import datetime
from odoo.api import Environment

class ApplicationService:
    def __init__(self, env: Environment):
        self.env = env
        self.AtsApplication = env['ats.application']
        self.AtsApplicantProfile = env['ats.applicant.profile']
        self.AtsJob = env['ats.job']

    def get_profile(self, user_id: int):
        return self.AtsApplicantProfile.search([('user_id', '=', user_id)], limit=1)

    def create_application(self, *, user_id: int, job_id: int):
        profile = self.get_profile(user_id=user_id)
        if not profile:
            raise ValueError("Applicant profile does not exist")
        existing = self.AtsApplication.search([
            ('job_id', '=', job_id),
            ('applicant_id', '=', profile.id)
        ], limit=1)
        if existing:
            return existing
        vals = {
            'job_id': job_id,
            'applicant_id': profile.id,
            'submitted_at': datetime.now(),
            'status': 'applied',
        }
        return self.AtsApplication.create(vals)

    def get_applications(self, *, user_id: int):
        profile = self.get_profile(user_id=user_id)
        if not profile:
            return self.AtsApplication.browse()
        return self.AtsApplication.search([('applicant_id', '=', profile.id)])

    def get_application(self, *, application_id: int):
        return self.AtsApplication.browse(application_id)

    def update_application_status(self, *, application_id: int, status: str):
        application = self.get_application(application_id=application_id)
        if not application.exists():
            raise ValueError("Application does not exist")
        application.status = status
        return application

    def delete_application(self, *, application_id: int):
        application = self.get_application(application_id=application_id)
        if application.exists():
            application.unlink()
            return True
        return False

    def search_jobs(self, *, keywords: str = None, location: str = None, job_type: str = None):
        domain = [('status', '=', 'published')]
        if keywords:
            domain += ['|', ('name', 'ilike', keywords), ('description', 'ilike', keywords)]
        if location:
            domain.append(('location', 'ilike', location))
        if job_type:
            domain.append(('job_type', '=', job_type))
        return self.AtsJob.search(domain)