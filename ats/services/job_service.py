from enum import Enum
from datetime import datetime, timedelta
from typing import Optional, List

from odoo import api, models
from odoo.exceptions import ValidationError

from ats.models.job import JobStatus, ApprovalStatus


from enum import Enum
from datetime import datetime, timedelta
from typing import Optional, List

from odoo import api, models
from odoo.exceptions import ValidationError

from ats.models.job import JobStatus, ApprovalStatus


class JobService:
    def __init__(self, env):
        self.env = env
        self.AtsJob = env['ats.job']
        self.AtsJobApproval = env['ats.job.approval']

    def create_job(
        self,
        *,
        title: str,
        description: str,
        department_id: int,
        lga_id: int,
        employment_type: str,
        application_deadline: Optional[str],
        salary_min: Optional[float],
        salary_max: Optional[float],
        currency_id: Optional[int],
        required_skill_ids: Optional[List[int]],
        created_by_id: int
    ):
        job_vals = {
            'name': title,
            'description': description,
            'status': JobStatus.DRAFT.value,
            'created_by': created_by_id,
            'department_id': department_id,
            'lga_id': lga_id,
            'employment_type': employment_type,
            'application_deadline': application_deadline,
            'salary_min': salary_min,
            'salary_max': salary_max,
            'currency_id': currency_id,
            'required_skill_ids': [(6, 0, required_skill_ids or [])],
            'last_status_update_at': datetime.now(),
        }
        job = self.AtsJob.create(job_vals)
        return job

    def update_job(
        self,
        job_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        department_id: Optional[int] = None,
        lga_id: Optional[int] = None,
        employment_type: Optional[str] = None,
        application_deadline: Optional[str] = None,
        salary_min: Optional[float] = None,
        salary_max: Optional[float] = None,
        currency_id: Optional[int] = None,
        required_skill_ids: Optional[List[int]] = None,
    ):
        job = self.AtsJob.browse(job_id)
        if not job.exists():
            raise ValidationError(f"Job {job_id} not found")

        if job.status not in [JobStatus.DRAFT.value, JobStatus.APPROVED.value]:
            raise ValidationError(f"Job {job_id} cannot be updated in status {job.status}")

        update_vals = {}
        if title is not None:
            update_vals['name'] = title
        if description is not None:
            update_vals['description'] = description
        if department_id is not None:
            update_vals['department_id'] = department_id
        if lga_id is not None:
            update_vals['lga_id'] = lga_id
        if employment_type is not None:
            update_vals['employment_type'] = employment_type
        if application_deadline is not None:
            update_vals['application_deadline'] = application_deadline
        if salary_min is not None:
            update_vals['salary_min'] = salary_min
        if salary_max is not None:
            update_vals['salary_max'] = salary_max
        if currency_id is not None:
            update_vals['currency_id'] = currency_id
        if required_skill_ids is not None:
            update_vals['required_skill_ids'] = [(6, 0, required_skill_ids)]

        if update_vals:
            update_vals['last_status_update_at'] = datetime.now()
            job.write(update_vals)

        return job

    def approve_job(self, job_id: int, approver_id: int, approve: bool, comment: Optional[str] = None):
        job = self.AtsJob.browse(job_id)
        if not job.exists():
            raise ValidationError(f"Job {job_id} not found")

        if job.status != JobStatus.DRAFT.value and approve:
            raise ValidationError(f"Only draft jobs can be approved")

        approval_status = ApprovalStatus.APPROVED.value if approve else ApprovalStatus.REJECTED.value

        # Record approval/rejection
        approval = self.AtsJobApproval.create({
            'job_id': job.id,
            'approver_id': approver_id,
            'status': approval_status,
            'comment': comment,
            'approved_at': datetime.now(),
        })

        # Update job status accordingly
        if approve:
            job.status = JobStatus.APPROVED.value
        else:
            job.status = JobStatus.DRAFT.value

        job.write({'last_status_update_at': datetime.now()})
        return job, approval

    def update_job_status(self, job_id: int, new_status: JobStatus):
        job = self.AtsJob.browse(job_id)
        if not job.exists():
            raise ValidationError(f"Job {job_id} not found")

        current_status = job.status

        valid_transitions = {
            JobStatus.APPROVED.value: [JobStatus.PUBLISHED.value],
            JobStatus.PUBLISHED.value: [JobStatus.CLOSED.value],
            JobStatus.CLOSED.value: [JobStatus.PUBLISHED.value],
            JobStatus.DRAFT.value: [JobStatus.APPROVED.value],  # no direct transitions unless via approval
            JobStatus.ARCHIVED.value: [JobStatus.DRAFT.value, JobStatus.APPROVED.value, JobStatus.PUBLISHED.value, JobStatus.CLOSED.value],
        }

        allowed_next = valid_transitions.get(current_status, [])

        if new_status == JobStatus.ARCHIVED:
            # Archiving is always allowed (manually or auto)
            pass
        elif new_status.value not in allowed_next:
            raise ValidationError(f"Invalid status transition from {current_status} to {new_status.value}")

        job.status = new_status.value
        job.write({'last_status_update_at': datetime.now()})
        return job

    def get_job(self, job_id: int):
        job = self.AtsJob.browse(job_id)
        if not job.exists():
            raise ValidationError(f"Job {job_id} not found")
        return job

    def list_jobs(self, filters: dict = None, limit: int = 50, offset: int = 0):
        domain = []
        if filters:
            for field, value in filters.items():
                domain.append((field, '=', value))

        jobs = self.AtsJob.search(domain, limit=limit, offset=offset, order='create_date desc')
        return jobs