from fastapi import APIRouter, Depends, HTTPException, status
from ats.services.applicant_service import ApplicantService
from ats.models.applicant import (
    ApplicantProfileCreate,
    ApplicantProfileUpdate,
    ApplicantProfileResponse,
    SkillCreate,
    SkillBase,
)
from ats.models.user import UserOut
from ats.security.auth_dependency import (
    get_current_user,
    require_role,
    get_odoo_env_dependency_async,
)
from ats.core.utils import run_in_thread

router = APIRouter(prefix="/v1/applicant", tags=["Applicant"])

# -----------------------------
# Profile Endpoints
# -----------------------------

@router.get(
    "/profile",
    response_model=ApplicantProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user's applicant profile"
)
async def get_profile(
    current_user: UserOut = Depends(require_role("applicant")),
    env = Depends(get_odoo_env_dependency_async)
):
    service = ApplicantService(env)
    profile = await run_in_thread(service.get_profile, user_id=current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Applicant profile not found")
    return profile

@router.post(
    "/profile",
    response_model=ApplicantProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new applicant profile"
)
async def create_profile(
    payload: ApplicantProfileCreate,
    current_user: UserOut = Depends(require_role("applicant")),
    env = Depends(get_odoo_env_dependency_async)
):
    service = ApplicantService(env)
    existing = await run_in_thread(service.get_profile, user_id=current_user.id)
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists")
    new_profile = await run_in_thread(
        service.create_profile,
        user_id=current_user.id,
        resume_url=payload.resume_url,
        skill_ids=payload.skill_ids,
        experience_years=payload.experience_years,
        status=payload.status
    )
    return new_profile

@router.put(
    "/profile",
    response_model=ApplicantProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Update current user's applicant profile"
)
async def update_profile(
    payload: ApplicantProfileUpdate,
    current_user: UserOut = Depends(require_role("applicant")),
    env = Depends(get_odoo_env_dependency_async)
):
    service = ApplicantService(env)
    updated = await run_in_thread(
        service.update_profile,
        user_id=current_user.id,
        resume_url=payload.resume_url,
        skill_ids=payload.skill_ids,
        experience_years=payload.experience_years,
        status=payload.status
    )
    return updated

@router.delete(
    "/profile",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete current user's applicant profile"
)
async def delete_profile(
    current_user: UserOut = Depends(require_role("applicant")),
    env = Depends(get_odoo_env_dependency_async)
):
    service = ApplicantService(env)
    deleted = await run_in_thread(service.delete_profile, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Profile not found or already deleted")
    return

# -----------------------------
# Skill Endpoints
# -----------------------------

@router.get(
    "/skills",
    response_model=list[SkillBase],
    status_code=status.HTTP_200_OK,
    summary="List all available skills"
)
async def list_skills(
    current_user: UserOut = Depends(require_role("applicant")),
    env = Depends(get_odoo_env_dependency_async)
):
    service = ApplicantService(env)
    return await run_in_thread(service.list_skills)

@router.post(
    "/skills",
    response_model=SkillBase,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new skill (if it doesn't exist)"
)
async def create_skill(
    payload: SkillCreate,
    current_user: UserOut = Depends(require_role("applicant")),
    env = Depends(get_odoo_env_dependency_async)
):
    service = ApplicantService(env)
    return await run_in_thread(service.create_skill, name=payload.name)