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

    def create_job(self, *, title: str, description: str, created_by_id: int):
        job_vals = {
            'name': title,
            'description': description,
            'status': JobStatus.DRAFT.value,
            'created_by': created_by_id,
            'last_status_update_at': datetime.now(),
        }
        job = self.AtsJob.create(job_vals)
        return job

    def update_job(self, job_id: int, updater_id: int, title: Optional[str] = None, description: Optional[str] = None):
        job = self.AtsJob.browse(job_id)
        if not job.exists():
            raise ValidationError(f"Job {job_id} not found")

        # Only allow editing if job is in draft or approved (not published or closed)
        if job.status not in [JobStatus.DRAFT.value, JobStatus.APPROVED.value]:
            raise ValidationError(f"Job {job_id} cannot be updated in status {job.status}")

        if title:
            job.name = title
        if description:
            job.description = description

        job.write({'last_status_update_at': datetime.now()})
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

    def publish_job(self, job_id: int, publisher_id: int):
        job = self.AtsJob.browse(job_id)
        if not job.exists():
            raise ValidationError(f"Job {job_id} not found")

        # Only approved jobs can be published
        if job.status != JobStatus.APPROVED.value:
            raise ValidationError(f"Only approved jobs can be published")

        job.status = JobStatus.PUBLISHED.value
        job.write({'last_status_update_at': datetime.now()})
        return job

    def close_job(self, job_id: int, closer_id: int):
        job = self.AtsJob.browse(job_id)
        if not job.exists():
            raise ValidationError(f"Job {job_id} not found")

        # Only published or closed jobs can be closed (closed jobs can be re-opened)
        if job.status not in [JobStatus.PUBLISHED.value, JobStatus.CLOSED.value]:
            raise ValidationError(f"Job {job_id} cannot be closed from status {job.status}")

        job.status = JobStatus.CLOSED.value
        job.write({'last_status_update_at': datetime.now()})
        return job

    def reopen_job(self, job_id: int, reopener_id: int):
        job = self.AtsJob.browse(job_id)
        if not job.exists():
            raise ValidationError(f"Job {job_id} not found")

        if job.status != JobStatus.CLOSED.value:
            raise ValidationError(f"Only closed jobs can be reopened")

        job.status = JobStatus.PUBLISHED.value
        job.write({'last_status_update_at': datetime.now()})
        return job

    def auto_archive_jobs(self):
        """Auto-archive jobs inactive for 90+ days."""
        cutoff_date = datetime.now() - timedelta(days=90)
        jobs_to_archive = self.AtsJob.search([
            ('status', 'in', [JobStatus.DRAFT.value, JobStatus.APPROVED.value, JobStatus.PUBLISHED.value, JobStatus.CLOSED.value]),
            ('last_status_update_at', '<', cutoff_date),
        ])
        for job in jobs_to_archive:
            job.status = JobStatus.ARCHIVED.value
            job.write({'last_status_update_at': datetime.now()})

        return jobs_to_archive

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