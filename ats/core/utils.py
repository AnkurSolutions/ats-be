# Thread pool for running sync Odoo service operations
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from fastapi import HTTPException

from ats.models.application import ApplicationResponse
from ats.services.applicant_service import ApplicantService
from ats.services.job_service import JobService

executor = ThreadPoolExecutor(max_workers=10)

async def run_in_thread(func, *args, **kwargs):
    """Helper to run sync functions in thread pool"""
    loop = asyncio.get_event_loop()
    if kwargs:
        # Use functools.partial to bind keyword arguments
        partial_func = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, partial_func)
    else:
        # If no kwargs, use the original approach
        return await loop.run_in_executor(executor, func, *args)
    
from typing import Any, Dict

async def serialize_job(job) -> Dict:
    return {
        "id": job.id,
        "title": job.name,
        "description": job.description,
        "status": job.status,
        "employment_type": job.employment_type,
        "application_deadline": job.application_deadline,
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "currency": {
            "id": job.currency_id.id,
            "name": job.currency_id.name,
            "symbol": job.currency_id.symbol,
        } if job.currency_id else None,
        "department": {
            "id": job.department_id.id,
            "name": job.department_id.name,
        } if job.department_id else None,
        "location": {
            "id": job.lga_id.id,
            "name": job.lga_id.name,
            "state": {
                "id": job.lga_id.state_id.id,
                "name": job.lga_id.state_id.name,
            } if job.lga_id.state_id else None,
        } if job.lga_id else None,
        "required_skills": [
            {"id": skill.id, "name": skill.name}
            for skill in job.required_skill_ids
        ],
        "created_by": {
            "id": job.created_by.id,
            "name": job.created_by.name,
            "email": job.created_by.email,
        },
        "last_status_update_at": job.last_status_update_at,
    }


def flatten_foreign_keys(record: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    """
    Flatten foreign key fields from (id, label) to just id.

    Args:
        record (dict): The Odoo record dict from `.read()`
        fields (list): List of fields to flatten

    Returns:
        dict: Updated record with flattened foreign key values
    """
    for field in fields:
        value = record.get(field)

        if isinstance(value, (tuple, list)) and len(value) >= 1:
            record[field] = value[0]
        elif value in (False, None):
            record[field] = None

    return record


def transform_profile_data(profile_data: dict) -> dict:
    def clean(value):
        return None if value is False else value

    return {
        'id': profile_data['id'],
        'user_id': profile_data['user_id'][0] if isinstance(profile_data['user_id'], tuple) else profile_data['user_id'],
        'resume_url': clean(profile_data.get('resume_url')),
        'skill_ids': profile_data.get('skill_ids', []),
        'tag_ids': profile_data.get('tag_ids', []),
        'experience_years': profile_data.get('experience_years', 0),
        'status': clean(profile_data.get('status', 'active')),
        'stage': clean(profile_data.get('stage', 'shortlisted')),
        'phone': clean(profile_data.get('phone')),
        'email': clean(profile_data.get('email')),
        'education_summary': clean(profile_data.get('education_summary')),
        'work_summary': clean(profile_data.get('work_summary')),
        'preferred_job_types': clean(profile_data.get('preferred_job_types')),
        'current_location': clean(profile_data.get('current_location')),
        'parse_metadata': profile_data.get('parse_metadata') or {},
    }

async def build_application_response(env, application):
    # Get the job record from ats.job with all required fields
    job_services = JobService(env)
    job = await run_in_thread(
        job_services.get_job, application['job_id']
    )
    job  = await serialize_job(job)
    # Get the applicant profile from ats.applicant.profile with required fields

    applicant = env['ats.applicant.profile'].browse(application['applicant_id'])
    profile_data = await run_in_thread(lambda: applicant.read([
            'id', 'user_id', 'resume_url', 'skill_ids', 'tag_ids', 'experience_years',
            'status', 'stage', 'phone', 'email', 'education_summary', 'work_summary',
            'preferred_job_types', 'current_location', 'parse_metadata'
        ])[0])
    applicant = transform_profile_data(profile_data)
    
    # Get tags from ats.application.tag
    tags = await run_in_thread(lambda: env['ats.application.tag'].browse(application['tag_ids']).read(['id', 'name']))
    # Get reviewed_by user from res.users (handle null case)
    reviewed_by = None
    if application['reviewed_by']:
        print("Here")
        reviewed_by_id = application['reviewed_by'][0] if isinstance(application['reviewed_by'], tuple) else application['reviewed_by']
        reviewed_by = await run_in_thread(lambda: env['res.users'].browse(reviewed_by_id).read(['id', 'name', 'email', 'create_date'])[0])

    return ApplicationResponse(
        id=application['id'],
        job=job,
        applicant=applicant,
        submitted_at=application['submitted_at'],
        status=application['status'],
        current_stage=application['current_stage'],
        reviewed_at=application['reviewed_at'],
        reviewed_by=reviewed_by,
        decision_notes=application['decision_notes'],
        source=application['source'],
        tags=tags,
        comment_ids=[],  # Add if implemented
        status_history_ids=[]  # Add if implemented
    )