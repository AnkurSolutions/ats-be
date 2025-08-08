from datetime import datetime
from odoo.api import Environment
from odoo.exceptions import ValidationError


class ApplicationService:
    VALID_TRANSITIONS = {
        'applied': ['shortlisted', 'rejected'],
        'shortlisted': ['interview_scheduled', 'rejected'],
        'interview_scheduled': ['offered', 'rejected'],
        'offered': ['hired', 'rejected'],
    }

    def __init__(self, env: Environment):
        self.env = env
        self.AtsApplication = env['ats.application']
        self.AtsApplicantProfile = env['ats.applicant.profile']
        self.AtsStatusHistory = env['ats.application.status.history']
        self.AtsApplicationTag = env['ats.application.tag']
        self.ResUsers = env['res.users']

    def get_profile(self, user_id: int):
        return self.AtsApplicantProfile.search([('user_id', '=', user_id)], limit=1)

    def get_application(self, *, application_id: int):
        return self.AtsApplication.browse(application_id)

    def get_applications(self, *, user_id: int):
        profile = self.get_profile(user_id=user_id)
        if not profile:
            return self.AtsApplication.browse()
        return self.AtsApplication.search([('applicant_id', '=', profile.id)])

    def get_all_applications(self):
        return self.AtsApplication.search([])

    def search_applications_by_job(self, job_id: int):
        return self.AtsApplication.search([('job_id', '=', job_id)])

    def create_application(self, *, user_id: int, job_id: int, source: str = None, tag_ids: list[int] = None):
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
            'current_stage': 'applied',
            'source': source,
        }

        if tag_ids:
            if not isinstance(tag_ids, list):
                raise ValueError("tag_ids must be a list of integers.")
            vals['tag_ids'] = [(6, 0, tag_ids)]

        application = self.AtsApplication.create(vals)

        self._log_status_history(
            application_id=application.id,
            from_status='applied',
            to_status='applied',
            user_id=user_id
        )

        return application

    def update_application_status(
        self, *, application_id: int, status: str, current_user_id: int,
        notes: str = None, tag_ids: list[int] = None
    ):
        application = self.get_application(application_id=application_id)
        if not application.exists():
            raise ValueError("Application does not exist")

        old_status = application.status

        # Validate transition
        if status != old_status:
            allowed = self.VALID_TRANSITIONS.get(old_status, [])
            if status not in allowed:
                raise ValidationError(f"Invalid transition from '{old_status}' to '{status}'")

        updates = {
            'status': status,
            'current_stage': status,
            'reviewed_at': datetime.now(),
            'reviewed_by': current_user_id,
            'decision_notes': notes,
        }

        application.write(updates)

        if tag_ids is not None:
            if not isinstance(tag_ids, list):
                raise ValueError("tag_ids must be a list of integers.")
            application.write({'tag_ids': [(6, 0, tag_ids)]})

        if status != old_status:
            self._log_status_history(
                application_id=application.id,
                from_status=old_status,
                to_status=status,
                user_id=current_user_id
            )

        return application

    def bulk_update_status(self, *, current_user_id: int, application_ids: list[int], status: str):
        applications = self.AtsApplication.browse(application_ids)
        if not applications:
            raise ValueError("No valid applications found")

        for app in applications:
            old_status = app.status

            # Validate transition
            if status != old_status:
                allowed = self.VALID_TRANSITIONS.get(old_status, [])
                if status not in allowed:
                    raise ValidationError(f"Invalid transition from '{old_status}' to '{status}'")

            updates = {
                'status': status,
                'current_stage': status,
                'reviewed_at': datetime.now(),
                'reviewed_by': current_user_id,
                'decision_notes': None,
            }

            app.write(updates)

            if app.tag_ids:
                app.write({'tag_ids': [(6, 0, app.tag_ids.ids)]})

            if status != old_status:
                self._log_status_history(
                    application_id=app.id,
                    from_status=old_status,
                    to_status=status,
                    user_id=current_user_id
                )

        return applications

    def delete_application(self, *, application_id: int):
        application = self.get_application(application_id=application_id)
        if application.exists():
            application.unlink()
            return True
        return False

    def get_status_history(self, *, application_id: int):
        try:
            return self.AtsStatusHistory.search([
                ('application_id', '=', application_id)
            ], order='changed_at asc')
        except Exception as e:
            raise ValueError(f"Failed to fetch status history: {str(e)}")

    def _log_status_history(self, *, application_id: int, from_status: str, to_status: str, user_id: int):
        try:
            self.AtsStatusHistory.create({
                'application_id': application_id,
                'from_status': from_status,
                'to_status': to_status,
                'changed_by': user_id,
                'changed_at': datetime.now()
            })
        except Exception as e:
            raise ValueError(f"Failed to log status change: {str(e)}")

    # ---------------- TAGGING SUPPORT ----------------

    def set_tags(self, *, application_id: int, tag_ids: list[int]):
        application = self.get_application(application_id=application_id)
        if not application.exists():
            raise ValueError("Application not found")

        application.write({'tag_ids': [(6, 0, tag_ids)]})
        return application

    def list_tags(self):
        return self.AtsApplicationTag.search([])

    def create_tag(self, name: str):
        name = name.strip()
        if not name:
            raise ValueError("Tag name must not be empty")

        existing = self.AtsApplicationTag.search([('name', '=', name)], limit=1)
        return existing if existing else self.AtsApplicationTag.create({'name': name})