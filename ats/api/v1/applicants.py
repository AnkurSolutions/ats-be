from fastapi import APIRouter, Depends, HTTPException, status
from ats.services.applicant_service import ApplicantService
from ats.models.applicant import (
    ApplicantOnboardRequest,
    ApplicantProfileUpdate,
    ApplicantProfileResponse,
)
from ats.models.user import UserOut
from ats.security.auth_dependency import (
    get_current_user,
    require_role,
    get_odoo_env_dependency_async,
)
from ats.core.utils import run_in_thread
from pydantic import ValidationError

router = APIRouter(prefix="/v1/applicant", tags=["Applicant"])

def transform_profile_data(profile_data: dict) -> dict:
    return {
        'id': profile_data['id'],
        'user_id': profile_data['user_id'][0] if isinstance(profile_data['user_id'], tuple) else profile_data['user_id'],
        'resume_url': profile_data['resume_url'] or None,
        'skill_ids': profile_data['skill_ids'] or [],
        'experience_years': profile_data['experience_years'] or 0,
        'status': profile_data['status'] or 'active'
    }

@router.get("/profile", response_model=ApplicantProfileResponse, status_code=status.HTTP_200_OK)
async def get_profile(current_user: UserOut = Depends(require_role("applicant"))):
    env, cr = await get_odoo_env_dependency_async()
    service = ApplicantService(env)

    try:
        profile = await run_in_thread(service.get_profile, user_id=current_user["id"])
        if not profile:
            raise HTTPException(status_code=404, detail="Applicant profile not found")

        profile_data = await run_in_thread(
            lambda: profile.read(['id', 'user_id', 'resume_url', 'skill_ids', 'experience_years', 'status'])[0]
        )
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
            resume_url=payload.resume_url,
            skill_ids=payload.skill_ids,
            experience_years=payload.experience_years,
            status=payload.status
        )

        profile_data = await run_in_thread(
            lambda: profile.read(['id', 'user_id', 'resume_url', 'skill_ids', 'experience_years', 'status'])[0]
        )
        await run_in_thread(cr.commit)
        return ApplicantProfileResponse(**transform_profile_data(profile_data))

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Missing required field: {str(e)}")
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
        update_data = {}
        if payload.resume_url is not None:
            update_data['resume_url'] = payload.resume_url
        if payload.skill_ids is not None:
            update_data['skill_ids'] = payload.skill_ids
        if payload.experience_years is not None:
            update_data['experience_years'] = payload.experience_years
        if payload.status is not None:
            update_data['status'] = payload.status

        updated_profile = await run_in_thread(
            service.update_profile,
            user_id=current_user["id"],
            **update_data
        )

        profile_data = await run_in_thread(
            lambda: updated_profile.read(['id', 'user_id', 'resume_url', 'skill_ids', 'experience_years', 'status'])[0]
        )
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