# Thread pool for running sync Odoo service operations
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial

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
    
from typing import Dict

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