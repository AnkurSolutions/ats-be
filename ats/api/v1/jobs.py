from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from ats.models.job import JobCreate, JobUpdate, JobOut
from ats.services.job_service import (
    create_job, get_job_by_id, list_jobs, update_job, delete_job
)
from ats.db.session import get_odoo_env_async

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("/", response_model=JobOut)
async def create_job_post(job: JobCreate):
    async with get_odoo_env_async() as env:
        new_job = create_job(env, job.model_dump())
        return new_job.read(['id', 'name', 'description', 'requirements', 'department_id', 'no_of_recruitment', 'create_date'])[0]

@router.get("/", response_model=list[JobOut])
async def get_all_jobs(
    department_id: Optional[int] = Query(None),
    name: Optional[str] = Query(None),
    limit: int = Query(100),
    offset: int = Query(0)
):
    async with get_odoo_env_async() as env:
        jobs = list_jobs(env, department_id=department_id, name=name, limit=limit, offset=offset)
        return jobs.read(['id', 'name', 'description', 'requirements', 'department_id', 'no_of_recruitment', 'create_date'])

@router.get("/{job_id}", response_model=JobOut)
async def get_job(job_id: int):
    async with get_odoo_env_async() as env:
        job = get_job_by_id(env, job_id)
        if not job.exists():
            raise HTTPException(status_code=404, detail="Job not found")
        return job.read(['id', 'name', 'description', 'requirements', 'department_id', 'no_of_recruitment', 'create_date'])[0]

@router.put("/{job_id}", response_model=JobOut)
async def update_job_post(job_id: int, job: JobUpdate):
    async with get_odoo_env_async() as env:
        updated = update_job(env, job_id, job.dict())
        if not updated:
            raise HTTPException(status_code=404, detail="Job not found")
        return updated.read(['id', 'name', 'description', 'requirements', 'department_id', 'no_of_recruitment', 'create_date'])[0]

@router.delete("/{job_id}")
async def delete_job_post(job_id: int):
    async with get_odoo_env_async() as env:
        deleted = delete_job(env, job_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Job not found")
        return {"status": "deleted"}