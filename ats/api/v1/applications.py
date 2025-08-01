from fastapi import APIRouter, Depends, status, HTTPException
from ats.models.application import (
    ApplicationCreate, ApplicationResponse, ApplicationUpdate
)
from ats.services.applicant_service import ApplicantService
from ats.core.utils import run_in_thread
from ats.security.auth_dependency import require_role, get_current_user, get_odoo_env_dependency_async
from odoo.exceptions import ValidationError

router = APIRouter(prefix="/v1/applications", tags=["Applications"])

@router.post(
    "/", 
    response_model=ApplicationResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Submit a new job application"
)
async def create_application(
    application_in: ApplicationCreate,
    current_user=Depends(require_role("applicant")),
    env=Depends(get_odoo_env_dependency_async),
):
    async def _create():
        service = ApplicantService(env)
        return service.create_application(user_id=current_user.id, job_id=application_in.job_id)
    return await run_in_thread(_create)

@router.get(
    "/", 
    response_model=list[ApplicationResponse], 
    status_code=status.HTTP_200_OK,
    summary="Get all job applications for current user"
)
async def get_applications(
    current_user=Depends(require_role("applicant")),
    env=Depends(get_odoo_env_dependency_async),
):
    async def _list():
        service = ApplicantService(env)
        return service.get_applications(user_id=current_user.id)
    return await run_in_thread(_list)

@router.get(
    "/{application_id}",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single job application by ID"
)
async def get_application(
    application_id: int,
    current_user=Depends(require_role("applicant")),
    env=Depends(get_odoo_env_dependency_async),
):
    async def _get():
        service = ApplicantService(env)
        return service.get_application(application_id=application_id)
    return await run_in_thread(_get)

@router.put(
    "/{application_id}",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
    summary="Update application status"
)
async def update_application_status(
    application_id: int,
    status_in: ApplicationUpdate,
    current_user=Depends(require_role("recruiter", "admin")),
    env=Depends(get_odoo_env_dependency_async),
):
    async def _update():
        service = ApplicantService(env)
        return service.update_application_status(application_id=application_id, status=status_in.status)
    return await run_in_thread(_update)

@router.delete(
    "/{application_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Withdraw or delete an application"
)
async def delete_application(
    application_id: int,
    current_user=Depends(require_role("applicant")),
    env=Depends(get_odoo_env_dependency_async),
):
    async def _delete():
        service = ApplicantService(env)
        result = service.delete_application(application_id=application_id)
        if not result:
            raise HTTPException(status_code=404, detail="Application not found")
    await run_in_thread(_delete)