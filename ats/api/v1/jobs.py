import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from ats.models.job import (
    JobCreate,
    JobUpdate,
    JobOut,
    JobApproveRequest,
    ApprovalStatus,
)
from ats.services.job_service import JobService
from fastapi.security import HTTPAuthorizationCredentials
from ats.security.auth_dependency import get_current_user, require_role, get_odoo_env_dependency_async
from odoo.exceptions import ValidationError

router = APIRouter(prefix="/v1/jobs", tags=["Jobs"])

# Thread pool for running sync Odoo service operations
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=10)

async def run_in_thread(func, *args, **kwargs):
    """Helper to run sync functions in thread pool"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, func, *args, **kwargs)

@router.post("/", response_model=JobOut, status_code=status.HTTP_201_CREATED, summary="Create a new job posting")
async def create_job(
    job_in: JobCreate,
    current_user=Depends(require_role("recruiter", "admin")),
):
    """Create a new job posting."""
    env, cr = None, None
    try:
        # Get environment asynchronously
        env, cr = await get_odoo_env_dependency_async()
        job_service = JobService(env)
        
        # Run sync operation in thread pool
        job = await run_in_thread(
            lambda: job_service.create_job(
                title=job_in.title,
                description=job_in.description,
                created_by_id=current_user["id"]
            )
        )
        
        # Get job data
        job_data = await run_in_thread(
            lambda: job.read(['id', 'name', 'description', 'status', 'created_by', 'create_date', 'last_status_update_at'])[0]
        )
        
        # Map fields to match Pydantic model
        job_data['title'] = job_data.pop('name')  # Map 'name' to 'title'
        
        # Get created_by user info
        if job_data.get('created_by'):
            created_by_id = job_data['created_by'][0] if isinstance(job_data['created_by'], tuple) else job_data['created_by']
            created_by_user = await run_in_thread(
                lambda: env['res.users'].browse(created_by_id).read(['id', 'name', 'email'])[0]
            )
            job_data['created_by'] = created_by_user
        else:
            job_data['created_by'] = {'id': current_user["id"], 'name': current_user.get("name", "Unknown"), 'email': current_user.get("email", "")}
        
        # Commit and close connection
        await run_in_thread(cr.commit)
        await run_in_thread(cr.close)
        
        return job_data
        
    except ValidationError as e:
        if cr:
            try:
                await run_in_thread(cr.rollback)
                await run_in_thread(cr.close)
            except:
                pass
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        if cr:
            try:
                await run_in_thread(cr.rollback)
                await run_in_thread(cr.close)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Error creating job: {str(e)}")


@router.get("/{job_id}", response_model=JobOut, summary="Get job by ID")
async def get_job(
    job_id: int,
    current_user=Depends(get_current_user),
):
    """Get a specific job by ID."""
    env, cr = None, None
    try:
        env, cr = await get_odoo_env_dependency_async()
        job_service = JobService(env)
        
        job = await run_in_thread(lambda: job_service.get_job(job_id))
        
        job_data = await run_in_thread(
            lambda: job.read(['id', 'name', 'description', 'status', 'created_by', 'create_date', 'last_status_update_at'])[0]
        )
        
        # Map fields to match Pydantic model
        job_data['title'] = job_data.pop('name')  # Map 'name' to 'title'
        
        # Get created_by user info
        if job_data.get('created_by'):
            created_by_id = job_data['created_by'][0] if isinstance(job_data['created_by'], tuple) else job_data['created_by']
            created_by_user = await run_in_thread(
                lambda: env['res.users'].browse(created_by_id).read(['id', 'name', 'email'])[0]
            )
            job_data['created_by'] = created_by_user
        else:
            job_data['created_by'] = {'id': 0, 'name': 'Unknown', 'email': ''}
        
        await run_in_thread(cr.close)
        return job_data
        
    except ValidationError as e:
        if cr:
            await run_in_thread(cr.close)
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        if cr:
            await run_in_thread(cr.close)
        raise HTTPException(status_code=500, detail=f"Error retrieving job: {str(e)}")


@router.put("/{job_id}", response_model=JobOut, summary="Update an existing job")
async def update_job(
    job_id: int,
    job_in: JobUpdate,
    current_user=Depends(require_role("recruiter", "admin")),
):
    """Update an existing job."""
    env, cr = None, None
    try:
        env, cr = await get_odoo_env_dependency_async()
        job_service = JobService(env)
        
        job = await run_in_thread(
            lambda: job_service.update_job(
                job_id=job_id,
                updater_id=current_user["id"],
                title=job_in.title,
                description=job_in.description
            )
        )
        
        job_data = await run_in_thread(
            lambda: job.read(['id', 'name', 'description', 'status', 'created_by', 'create_date', 'last_status_update_at'])[0]
        )
        
        # Map fields to match Pydantic model
        job_data['title'] = job_data.pop('name')  # Map 'name' to 'title'
        
        # Get created_by user info
        if job_data.get('created_by'):
            created_by_id = job_data['created_by'][0] if isinstance(job_data['created_by'], tuple) else job_data['created_by']
            created_by_user = await run_in_thread(
                lambda: env['res.users'].browse(created_by_id).read(['id', 'name', 'email'])[0]
            )
            job_data['created_by'] = created_by_user
        else:
            job_data['created_by'] = {'id': 0, 'name': 'Unknown', 'email': ''}
        
        await run_in_thread(cr.commit)
        await run_in_thread(cr.close)
        
        return job_data
        
    except ValidationError as e:
        if cr:
            try:
                await run_in_thread(cr.rollback)
                await run_in_thread(cr.close)
            except:
                pass
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        if cr:
            try:
                await run_in_thread(cr.rollback)
                await run_in_thread(cr.close)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Error updating job: {str(e)}")


@router.post("/{job_id}/approve", response_model=JobOut, summary="Approve or reject a job posting")
async def approve_job(
    job_id: int,
    approval: JobApproveRequest,
    current_user=Depends(require_role("hr")),
):
    """Approve or reject a job posting."""
    env, cr = None, None
    try:
        env, cr = await get_odoo_env_dependency_async()
        job_service = JobService(env)
        
        job, _ = await run_in_thread(
            lambda: job_service.approve_job(
                job_id=job_id,
                approver_id=current_user["id"],
                approve=(approval.status == ApprovalStatus.APPROVED),
                comment=approval.comment
            )
        )
        
        job_data = await run_in_thread(
            lambda: job.read(['id', 'name', 'description', 'status', 'created_by', 'create_date', 'last_status_update_at'])[0]
        )
        
        # Map fields to match Pydantic model
        job_data['title'] = job_data.pop('name')  # Map 'name' to 'title'
        
        # Get created_by user info
        if job_data.get('created_by'):
            created_by_id = job_data['created_by'][0] if isinstance(job_data['created_by'], tuple) else job_data['created_by']
            created_by_user = await run_in_thread(
                lambda: env['res.users'].browse(created_by_id).read(['id', 'name', 'email'])[0]
            )
            job_data['created_by'] = created_by_user
        else:
            job_data['created_by'] = {'id': 0, 'name': 'Unknown', 'email': ''}
        
        await run_in_thread(cr.commit)
        await run_in_thread(cr.close)
        
        return job_data
        
    except ValidationError as e:
        if cr:
            try:
                await run_in_thread(cr.rollback)
                await run_in_thread(cr.close)
            except:
                pass
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        if cr:
            try:
                await run_in_thread(cr.rollback)
                await run_in_thread(cr.close)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Error approving job: {str(e)}")


@router.post("/{job_id}/publish", response_model=JobOut, summary="Publish an approved job")
async def publish_job(
    job_id: int,
    current_user=Depends(require_role("admin")),
):
    """Publish an approved job."""
    env, cr = None, None
    try:
        env, cr = await get_odoo_env_dependency_async()
        job_service = JobService(env)
        
        job = await run_in_thread(
            lambda: job_service.publish_job(
                job_id=job_id,
                publisher_id=current_user["id"]
            )
        )
        
        job_data = await run_in_thread(
            lambda: job.read(['id', 'name', 'description', 'status', 'created_by', 'create_date', 'last_status_update_at'])[0]
        )
        
        # Map fields to match Pydantic model
        job_data['title'] = job_data.pop('name')  # Map 'name' to 'title'
        
        # Get created_by user info
        if job_data.get('created_by'):
            created_by_id = job_data['created_by'][0] if isinstance(job_data['created_by'], tuple) else job_data['created_by']
            created_by_user = await run_in_thread(
                lambda: env['res.users'].browse(created_by_id).read(['id', 'name', 'email'])[0]
            )
            job_data['created_by'] = created_by_user
        else:
            job_data['created_by'] = {'id': 0, 'name': 'Unknown', 'email': ''}
        
        await run_in_thread(cr.commit)
        await run_in_thread(cr.close)
        
        return job_data
        
    except ValidationError as e:
        if cr:
            try:
                await run_in_thread(cr.rollback)
                await run_in_thread(cr.close)
            except:
                pass
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        if cr:
            try:
                await run_in_thread(cr.rollback)
                await run_in_thread(cr.close)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Error publishing job: {str(e)}")


@router.post("/{job_id}/close", response_model=JobOut, summary="Close a published job")
async def close_job(
    job_id: int,
    current_user=Depends(require_role("hr", "admin")),
):
    """Close a published job."""
    env, cr = None, None
    try:
        env, cr = await get_odoo_env_dependency_async()
        job_service = JobService(env)
        
        job = await run_in_thread(
            lambda: job_service.close_job(
                job_id=job_id,
                closer_id=current_user["id"]
            )
        )
        
        job_data = await run_in_thread(
            lambda: job.read(['id', 'name', 'description', 'status', 'created_by', 'create_date', 'last_status_update_at'])[0]
        )
        
        # Map fields to match Pydantic model
        job_data['title'] = job_data.pop('name')  # Map 'name' to 'title'
        
        # Get created_by user info
        if job_data.get('created_by'):
            created_by_id = job_data['created_by'][0] if isinstance(job_data['created_by'], tuple) else job_data['created_by']
            created_by_user = await run_in_thread(
                lambda: env['res.users'].browse(created_by_id).read(['id', 'name', 'email'])[0]
            )
            job_data['created_by'] = created_by_user
        else:
            job_data['created_by'] = {'id': 0, 'name': 'Unknown', 'email': ''}
        
        await run_in_thread(cr.commit)
        await run_in_thread(cr.close)
        
        return job_data
        
    except ValidationError as e:
        if cr:
            try:
                await run_in_thread(cr.rollback)
                await run_in_thread(cr.close)
            except:
                pass
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        if cr:
            try:
                await run_in_thread(cr.rollback)
                await run_in_thread(cr.close)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Error closing job: {str(e)}")


@router.post("/{job_id}/reopen", response_model=JobOut, summary="Reopen a closed job")
async def reopen_job(
    job_id: int,
    current_user=Depends(require_role("hr", "admin")),
):
    """Reopen a closed job."""
    env, cr = None, None
    try:
        env, cr = await get_odoo_env_dependency_async()
        job_service = JobService(env)
        
        job = await run_in_thread(
            lambda: job_service.reopen_job(
                job_id=job_id,
                reopener_id=current_user["id"]
            )
        )
        
        job_data = await run_in_thread(
            lambda: job.read([
                'id',
                'name',
                'description',
                'status',
                'created_by',
                'last_status_update_at'
            ])[0]
        )

        job_data['title'] = job_data.pop('name')

        # Convert Many2one tuple (14, 'Jane Doe') to dict
        if isinstance(job_data['created_by'], tuple):
            job_data['created_by'] = {
                "id": job_data['created_by'][0],
                "name": job_data['created_by'][1]
            }
        
        await run_in_thread(cr.commit)
        await run_in_thread(cr.close)
        
        return job_data
        
    except ValidationError as e:
        if cr:
            try:
                await run_in_thread(cr.rollback)
                await run_in_thread(cr.close)
            except:
                pass
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        if cr:
            try:
                await run_in_thread(cr.rollback)
                await run_in_thread(cr.close)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Error reopening job: {str(e)}")


@router.get("/", response_model=List[JobOut], summary="List jobs with optional filtering")
async def list_jobs(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user=Depends(get_current_user),
):
    """List jobs with optional filtering."""
    env, cr = None, None
    try:
        env, cr = await get_odoo_env_dependency_async()
        job_service = JobService(env)
        
        filters = {}
        if status:
            filters['status'] = status

        jobs = await run_in_thread(
            lambda: job_service.list_jobs(
                filters=filters,
                limit=limit,
                offset=skip
            )
        )
        
        # Read job data for all jobs
        jobs_data = await run_in_thread(
            lambda: jobs.read(['id', 'name', 'description', 'status', 'created_by', 'create_date', 'last_status_update_at'])
        )
        
        # Map fields and get created_by info for each job
        for job_data in jobs_data:
            job_data['title'] = job_data.pop('name')  # Map 'name' to 'title'
            
            # Get created_by user info
            if job_data.get('created_by'):
                created_by_id = job_data['created_by'][0] if isinstance(job_data['created_by'], tuple) else job_data['created_by']
                created_by_user = await run_in_thread(
                    lambda: env['res.users'].browse(created_by_id).read(['id', 'name', 'email'])[0]
                )
                job_data['created_by'] = created_by_user
            else:
                job_data['created_by'] = {'id': 0, 'name': 'Unknown', 'email': ''}
        
        await run_in_thread(cr.close)
        
        return jobs_data
        
    except Exception as e:
        if cr:
            await run_in_thread(cr.close)
        raise HTTPException(status_code=500, detail=f"Error listing jobs: {str(e)}")