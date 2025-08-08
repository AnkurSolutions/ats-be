from fastapi import APIRouter, Depends, HTTPException, status
from ats.services.applicant_service import ApplicantService
from ats.models.applicant import (
    ApplicantOnboardRequest,
    ApplicantProfileUpdate,
    ApplicantProfileResponse,
)
from ats.models.user import UserOut
from ats.security.auth_dependency import (
    require_role,
    get_odoo_env_dependency_async,
)
from ats.core.utils import run_in_thread, transform_profile_data
from pydantic import ValidationError

router = APIRouter(prefix="/v1/applicant", tags=["Applicant"])

@router.get("/profile", response_model=ApplicantProfileResponse, status_code=status.HTTP_200_OK)
async def get_profile(current_user: UserOut = Depends(require_role("applicant"))):
    env, cr = await get_odoo_env_dependency_async()
    service = ApplicantService(env)

    try:
        profile = await run_in_thread(service.get_profile, user_id=current_user["id"])
        if not profile:
            raise HTTPException(status_code=404, detail="Applicant profile not found")

        profile_data = await run_in_thread(lambda: profile.read([
            'id', 'user_id', 'resume_url', 'skill_ids', 'tag_ids', 'experience_years',
            'status', 'stage', 'phone', 'email', 'education_summary', 'work_summary',
            'preferred_job_types', 'current_location', 'parse_metadata'
        ])[0])

        return ApplicantProfileResponse(**transform_profile_data(profile_data))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch profile: {str(e)}")
    finally:
        await run_in_thread(cr.close)

@router.post("/onboard", response_model=ApplicantProfileResponse, status_code=status.HTTP_201_CREATED)
async def onboard_applicant(
    payload: ApplicantOnboardRequest,
    current_user: UserOut = Depends(require_role("applicant")),
):
    env, cr = await get_odoo_env_dependency_async()
    service = ApplicantService(env)

    try:
        profile = await run_in_thread(
            service.onboard_applicant,
            user=current_user,
            **payload.model_dump(exclude_unset=True)
        )

        profile_data = await run_in_thread(lambda: profile.read([
            'id', 'user_id', 'resume_url', 'skill_ids', 'tag_ids', 'experience_years',
            'status', 'stage', 'phone', 'email', 'education_summary', 'work_summary',
            'preferred_job_types', 'current_location', 'parse_metadata'
        ])[0])

        await run_in_thread(cr.commit)
        return ApplicantProfileResponse(**transform_profile_data(profile_data))

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        await run_in_thread(cr.close)

@router.put("/profile", response_model=ApplicantProfileResponse, status_code=status.HTTP_200_OK)
async def update_profile(
    payload: ApplicantProfileUpdate,
    current_user: UserOut = Depends(require_role("applicant")),
):
    env, cr = await get_odoo_env_dependency_async()
    service = ApplicantService(env)

    try:
        updated_profile = await run_in_thread(
            service.update_profile,
            user_id=current_user["id"],
            **payload.model_dump(exclude_unset=True)
        )

        profile_data = await run_in_thread(lambda: updated_profile.read([
            'id', 'user_id', 'resume_url', 'skill_ids', 'tag_ids', 'experience_years',
            'status', 'stage', 'phone', 'email', 'education_summary', 'work_summary',
            'preferred_job_types', 'current_location', 'parse_metadata'
        ])[0])

        await run_in_thread(cr.commit)
        return ApplicantProfileResponse(**transform_profile_data(profile_data))

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")
    finally:
        await run_in_thread(cr.close)

@router.delete("/profile", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(current_user: UserOut = Depends(require_role("applicant"))):
    env, cr = await get_odoo_env_dependency_async()
    service = ApplicantService(env)

    try:
        deleted = await run_in_thread(service.delete_profile, user_id=current_user["id"])
        if not deleted:
            raise HTTPException(status_code=404, detail="Profile not found or already deleted")

        await run_in_thread(cr.commit)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete profile: {str(e)}")
    finally:
        await run_in_thread(cr.close)