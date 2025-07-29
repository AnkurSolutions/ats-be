from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ats.models.application import ApplicationCreate, ApplicationUpdate, ApplicationOut, PublicApplication
from ats.services.application_service import (
    create_application, get_application_by_id, update_application, delete_application, list_applications,
    submit_public_application
)
from ats.db.session import get_odoo_env_async

router = APIRouter(prefix="/applications", tags=["Applications"])

@router.post("/", response_model=ApplicationOut)
async def create_app(payload: ApplicationCreate):
    async with get_odoo_env_async() as env:
        app = create_application(env, payload.model_dump())
        return app.read(['id', 'name', 'email_from', 'job_id', 'partner_name', 'description', 'create_date'])[0]

@router.get("/", response_model=list[ApplicationOut])
async def list_all(
    job_id: Optional[int] = Query(None),
    email: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    limit: int = Query(100),
    offset: int = Query(0)
):
    async with get_odoo_env_async() as env:
        apps = list_applications(
            env,
            job_id=job_id,
            email=email,
            name=name,
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        return apps.read([
            'id', 'name', 'email_from', 'job_id',
            'partner_name', 'description', 'create_date'
        ])

@router.get("/{app_id}", response_model=ApplicationOut)
async def get_app(app_id: int):
    async with get_odoo_env_async() as env:
        app = get_application_by_id(env, app_id)
        if not app.exists():
            raise HTTPException(status_code=404, detail="Application not found")
        return app.read(['id', 'name', 'email_from', 'job_id', 'partner_name', 'description', 'create_date'])[0]

@router.put("/{app_id}", response_model=ApplicationOut)
async def update_app(app_id: int, payload: ApplicationUpdate):
    async with get_odoo_env_async() as env:
        updated = update_application(env, app_id, payload.model_dump(exclude_unset=True))
        if not updated:
            raise HTTPException(status_code=404, detail="Application not found")
        return updated.read(['id', 'name', 'email_from', 'job_id', 'partner_name', 'description', 'create_date'])[0]

@router.delete("/{app_id}")
async def delete_app(app_id: int):
    async with get_odoo_env_async() as env:
        deleted = delete_application(env, app_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Application not found")
        return {"status": "deleted"}

@router.post("/jobs/{job_id}/apply")
async def apply_to_job(job_id: int, payload: PublicApplication):
    async with get_odoo_env_async() as env:
        job = env['hr.job'].browse(job_id)
        if not job.exists():
            raise HTTPException(status_code=404, detail="Job not found")

        application = submit_public_application(env, job_id, payload.dict())
        return {
            "status": "success",
            "application_id": application.id,
            "message": "Application submitted successfully."
        }