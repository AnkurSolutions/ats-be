from fastapi import APIRouter, Depends, status, HTTPException
from ats.models.application import (
    ApplicationCreate, ApplicationResponse, ApplicationTagUpdate,
    ApplicationUpdate, BulkStatusUpdateRequest, TagBase, TagCreate,
    ApplicationStatusHistory
)
from ats.services.application_service import ApplicationService
from ats.core.utils import build_application_response, flatten_foreign_keys, run_in_thread, serialize_job, transform_profile_data
from ats.security.auth_dependency import require_role, get_odoo_env_dependency_async

router = APIRouter(prefix="/v1/applications", tags=["Applications"])

READ_FIELDS = [
    "id", "job_id", "applicant_id", "submitted_at", "status",
    "current_stage", "reviewed_at", "reviewed_by", "decision_notes",
    "tag_ids", "source"
]

@router.post("/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
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
            job_id=application_in.job_id,
            source=application_in.source,
            tag_ids=application_in.tag_ids
        )
        await run_in_thread(cr.commit)
        application = await run_in_thread(lambda: application.read(READ_FIELDS)[0])
        flatten_foreign_keys(application, ["job_id", "applicant_id", "reviewed_by", "decision_notes", "reviewed_at", "source"])
        return await build_application_response(env, application)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create application: {str(e)}")
    finally:
        await run_in_thread(cr.close)

@router.get("/", response_model=list[ApplicationResponse], status_code=status.HTTP_200_OK)
async def get_applications(current_user=Depends(require_role("applicant", "recruiter", "admin", "hr"))):
    env, cr = await get_odoo_env_dependency_async()
    service = ApplicationService(env)
    try:
        if current_user['role'] in ("recruiter", "admin", "hr"):
            applications = await run_in_thread(service.get_all_applications)
        else:
            applications = await run_in_thread(service.get_applications, user_id=current_user['id'])
        applications = await run_in_thread(lambda: applications.read(READ_FIELDS))
        applications = [flatten_foreign_keys(app, ["job_id", "applicant_id", "reviewed_by", "decision_notes", "reviewed_at", "source"]) for app in applications]
        if not applications:
            return []
        return [await build_application_response(env, app) for app in applications]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve applications: {str(e)}")
    finally:
        await run_in_thread(cr.close)

@router.get("/{application_id}", response_model=ApplicationResponse, status_code=status.HTTP_200_OK)
async def get_application(application_id: int, current_user=Depends(require_role("applicant"))):
    env, cr = await get_odoo_env_dependency_async()
    service = ApplicationService(env)
    try:
        application = await run_in_thread(service.get_application, application_id=application_id)
        if not application.exists():
            raise HTTPException(status_code=404, detail="Application not found")
        application = await run_in_thread(lambda: application.read(READ_FIELDS)[0])
        application = flatten_foreign_keys(application, ["job_id", "applicant_id", "reviewed_by", "decision_notes", "reviewed_at", "source"])
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        await run_in_thread(cr.commit)
        return await build_application_response(env, application)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve application: {str(e)}")
    finally:
        await run_in_thread(cr.close)

@router.put("/{application_id}", response_model=ApplicationResponse, status_code=status.HTTP_200_OK)
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
            status=status_in.status,
            current_stage=status_in.current_stage,
            notes=status_in.decision_notes,
            tag_ids=status_in.tag_ids,
            current_user_id=current_user["id"]
        )
        await run_in_thread(cr.commit)
        application = await run_in_thread(lambda: application.read(READ_FIELDS)[0])
        application = flatten_foreign_keys(application, ["job_id", "applicant_id", "reviewed_by", "decision_notes", "reviewed_at", "source"])
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        await run_in_thread(cr.commit)
        # Log status history
        await run_in_thread(
            service._log_status_history,
            application_id=application.id,
            from_status=status_in.status,
            to_status=status_in.current_stage,
            user_id=current_user["id"]
        )
        await run_in_thread(cr.commit)
        # Return the updated application response
        return await build_application_response(env, application)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update application status: {str(e)}")
    finally:
        await run_in_thread(cr.close)

@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(application_id: int, current_user=Depends(require_role("applicant"))):
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

@router.get("/by-job/{job_id}", response_model=list[ApplicationResponse], status_code=status.HTTP_200_OK)
async def get_applications_by_job(job_id: int, current_user=Depends(require_role("recruiter", "admin"))):
    env, cr = await get_odoo_env_dependency_async()
    service = ApplicationService(env)
    try:
        applications = await run_in_thread(service.search_applications_by_job, job_id=job_id)
        applications = await run_in_thread(lambda: applications.read(READ_FIELDS))
        applications = [flatten_foreign_keys(app, ["job_id", "applicant_id", "reviewed_by", "decision_notes", "reviewed_at", "source"]) for app in applications]
        if not applications:
            return []
        await run_in_thread(cr.commit)
        return [await build_application_response(env, app) for app in applications]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve applications: {str(e)}")
    finally:
        await run_in_thread(cr.close)

@router.put("/bulk/status", response_model=list[ApplicationResponse], status_code=status.HTTP_200_OK)
async def bulk_update_status(
    payload: BulkStatusUpdateRequest,
    current_user=Depends(require_role("recruiter", "admin")),
):
    env, cr = await get_odoo_env_dependency_async()
    service = ApplicationService(env)
    try:
        updated = await run_in_thread(
            service.bulk_update_status,
            current_user_id=current_user["id"],
            application_ids=payload.application_ids,
            status=payload.status
        )
        await run_in_thread(cr.commit)
        return [await build_application_response(env, app) for app in updated]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Bulk update failed: {str(e)}")
    finally:
        await run_in_thread(cr.close)

@router.put("/{application_id}/tags", response_model=ApplicationResponse, status_code=status.HTTP_200_OK)
async def set_application_tags(
    application_id: int,
    payload: ApplicationTagUpdate,
    current_user=Depends(require_role("recruiter", "admin")),
):
    env, cr = await get_odoo_env_dependency_async()
    service = ApplicationService(env)
    try:
        application = await run_in_thread(
            service.set_tags,
            application_id=application_id,
            tag_ids=payload.tag_ids
        )
        await run_in_thread(cr.commit)
        return await build_application_response(env, application)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update tags: {str(e)}")
    finally:
        await run_in_thread(cr.close)

@router.get("/tags", response_model=list[TagBase], status_code=status.HTTP_200_OK)
async def list_tags(current_user=Depends(require_role("recruiter", "admin"))):
    env, cr = await get_odoo_env_dependency_async()
    service = ApplicationService(env)
    try:
        tags = await run_in_thread(service.list_tags)
        tag_data = await run_in_thread(lambda: tags.read(["id", "name"]))
        return [TagBase(**tag) for tag in tag_data]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to list tags: {str(e)}")
    finally:
        await run_in_thread(cr.close)

@router.post("/tags", response_model=TagBase, status_code=status.HTTP_201_CREATED)
async def create_tag(payload: TagCreate, current_user=Depends(require_role("admin", "hr"))):
    env, cr = await get_odoo_env_dependency_async()
    service = ApplicationService(env)
    try:
        tag = await run_in_thread(service.create_tag, name=payload.name)
        tag_data = await run_in_thread(lambda: tag.read(["id", "name"])[0])
        await run_in_thread(cr.commit)
        return TagBase(**tag_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create tag: {str(e)}")
    finally:
        await run_in_thread(cr.close)

@router.get("/{application_id}/history", response_model=list[ApplicationStatusHistory], status_code=status.HTTP_200_OK)
async def get_application_status_history(
    application_id: int,
    current_user=Depends(require_role("recruiter", "admin", "applicant")),
):
    env, cr = await get_odoo_env_dependency_async()
    service = ApplicationService(env)
    try:
        records = await run_in_thread(service.get_status_history, application_id=application_id)
        history_data = await run_in_thread(lambda: records.read([
            "id", "application_id", "from_status", "to_status", "changed_by", "changed_at"
        ]))
        
        # Transform the data to handle Odoo's tuple format
        transformed_data = []
        for record in history_data:
            # Handle application_id if it's a tuple
            if isinstance(record['application_id'], tuple):
                record['application_id'] = record['application_id'][0]
            
            # Handle changed_by if it's a tuple - create UserOut object
            if isinstance(record['changed_by'], tuple):
                user_id, user_name = record['changed_by']
                # You'll need to fetch the full user data or create a minimal UserOut
                record['changed_by'] = {
                    'id': user_id,
                    'name': user_name,
                }
            
            transformed_data.append(record)
        
        return [ApplicationStatusHistory(**record) for record in transformed_data]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get history: {str(e)}")
    finally:
        await run_in_thread(cr.close)