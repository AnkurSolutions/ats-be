from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from ats.db.session import get_odoo_env_dependency_async
from ats.models.user import UserOut
from ats.security.auth_dependency import require_role
from odoo import SUPERUSER_ID
from odoo.exceptions import ValidationError

from ats.models.job import JobApproveRequest, JobCreate, JobOut, JobUpdate, JobStatusUpdateRequest
from ats.services.job_service import JobService
from ats.core.utils import run_in_thread, serialize_job

router = APIRouter(prefix="/v1/jobs", tags=["Jobs"])


@router.post("/", response_model=JobOut)
async def create_job(job_in: JobCreate, current_user=Depends(require_role("recruiter", "admin"))):
    env, cr = await get_odoo_env_dependency_async()
    try:
        job_service = JobService(env)
        job = await run_in_thread(lambda: job_service.create_job(**job_in.model_dump(), created_by_id=current_user["id"]))
        job_data = await serialize_job(job)
        await run_in_thread(cr.commit)
        return job_data
    except Exception as e:
        await run_in_thread(cr.rollback)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await run_in_thread(cr.close)


@router.get("/", response_model=List[JobOut])
async def list_jobs(
    status: Optional[str] = Query(None),
    department_id: Optional[int] = Query(None),
    lga_id: Optional[int] = Query(None),
    employment_type: Optional[str] = Query(None),
    currency_id: Optional[int] = Query(None),
    created_by: Optional[int] = Query(None),
    limit: int = Query(50, ge=1),
    offset: int = Query(0, ge=0),
):
    env, cr = await get_odoo_env_dependency_async()
    try:
        filters = {}
        if status:
            filters['status'] = status
        if department_id:
            filters['department_id'] = department_id
        if lga_id:
            filters['lga_id'] = lga_id
        if employment_type:
            filters['employment_type'] = employment_type
        if currency_id:
            filters['currency_id'] = currency_id
        if created_by:
            filters['created_by'] = created_by

        jobs = JobService(env).list_jobs(filters, limit=limit, offset=offset)
        return [await serialize_job(job) for job in jobs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await run_in_thread(cr.close)


@router.get("/{job_id}", response_model=JobOut)
async def get_job(job_id: int, current_user: UserOut = Depends(require_role("recruiter", "admin"))):
    env, cr = await get_odoo_env_dependency_async()
    try:
        job_service = JobService(env)
        job = await run_in_thread(lambda: job_service.get_job(job_id))
        job_data = await serialize_job(job)
        return job_data
    except ValidationError as e:
        raise HTTPException(status_code=404, detail=str(e))
    finally:
        await run_in_thread(cr.close)


@router.put("/{job_id}", response_model=JobOut)
async def update_job(job_id: int, job_in: JobUpdate, current_user: UserOut = Depends(require_role("recruiter", "admin"))):
    env, cr = await get_odoo_env_dependency_async()
    try:
        job_service = JobService(env)
        job = await run_in_thread(lambda: job_service.update_job(job_id=job_id, **job_in.model_dump(exclude_unset=True)))
        job_data = await serialize_job(job)
        await run_in_thread(cr.commit)
        return job_data
    except Exception as e:
        await run_in_thread(cr.rollback)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await run_in_thread(cr.close)


@router.patch("/{job_id}/status", response_model=JobOut)
async def change_job_status(job_id: int, req: JobStatusUpdateRequest, current_user: UserOut = Depends(require_role("admin", "hr"))):
    env, cr = await get_odoo_env_dependency_async()
    try:
        job_service = JobService(env)
        job = await run_in_thread(lambda: job_service.update_job_status(job_id, req.status))
        job_data = await serialize_job(job)
        await run_in_thread(cr.commit)
        return job_data
    except Exception as e:
        await run_in_thread(cr.rollback)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await run_in_thread(cr.close)

@router.post("/{job_id}/approve", response_model=JobOut)
async def approve_job(job_id: int, req: JobApproveRequest, current_user: UserOut = Depends(require_role("admin", "hr"))):
    try:
        env, cr = await get_odoo_env_dependency_async()
        job, _approval = JobService(env).approve_job(
            job_id=job_id,
            approver_id=SUPERUSER_ID,
            approve=(req.status == "approved"),
            comment=req.comment,
        )
        return await serialize_job(job)
    except ValidationError as e:
        await run_in_thread(cr.rollback)
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        await run_in_thread(cr.rollback)
        raise HTTPException(status_code=500, detail=str(e))
    except HTTPException as e:
        await run_in_thread(cr.rollback)
        raise e
    finally:
        await run_in_thread(cr.close)