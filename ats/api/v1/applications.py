from fastapi import APIRouter, Depends, status, HTTPException
from ats.models.application import (
    ApplicationCreate, ApplicationResponse, ApplicationUpdate
)
from ats.services.application_service import ApplicationService
from ats.core.utils import run_in_thread, flatten_foreign_keys
from ats.security.auth_dependency import require_role, get_odoo_env_dependency_async
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
):
    env, cr = await get_odoo_env_dependency_async()
    service = ApplicationService(env)
    try:
        application = await run_in_thread(
            service.create_application,
            user_id=current_user["id"],
            job_id=application_in.job_id
        )
        await run_in_thread(cr.commit)

        application_data = await run_in_thread(lambda: application.read([
            "id", "job_id", "applicant_id", "submitted_at", "status"
        ])[0])

        # Flatten foreign keys
        flatten_foreign_keys(application_data, ["job_id", "applicant_id"])

        return ApplicationResponse(**application_data)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create application: {str(e)}")
    finally:
        await run_in_thread(cr.close)

@router.get(
    "/", 
    response_model=list[ApplicationResponse], 
    status_code=status.HTTP_200_OK,
    summary="Get all job applications for current user"
)
async def get_applications(current_user=Depends(require_role("applicant"))):
    env, cr = await get_odoo_env_dependency_async()
    service = ApplicationService(env)
    try:
        return await run_in_thread(service.get_applications, user_id=current_user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve applications: {str(e)}")
    finally:
        await run_in_thread(cr.close)

@router.get(
    "/{application_id}",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single job application by ID"
)
async def get_application(
    application_id: int,
    current_user=Depends(require_role("applicant")),
):
    env, cr = await get_odoo_env_dependency_async()
    service = ApplicationService(env)
    try:
        return await run_in_thread(service.get_application, application_id=application_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve application: {str(e)}")
    finally:
        await run_in_thread(cr.close)

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
):
    env, cr = await get_odoo_env_dependency_async()
    service = ApplicationService(env)
    try:
        application = await run_in_thread(
            service.update_application_status,
            application_id=application_id,
            status=status_in.status
        )
        await run_in_thread(cr.commit)
        return application
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update application status: {str(e)}")
    finally:
        await run_in_thread(cr.close)

@router.delete(
    "/{application_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Withdraw or delete an application"
)
async def delete_application(
    application_id: int,
    current_user=Depends(require_role("applicant")),
):
    env, cr = await get_odoo_env_dependency_async()
    service = ApplicationService(env)
    try:
        result = await run_in_thread(service.delete_application, application_id=application_id)
        if not result:
            raise HTTPException(status_code=404, detail="Application not found")
        await run_in_thread(cr.commit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to delete application: {str(e)}")
    finally:
        await run_in_thread(cr.close)