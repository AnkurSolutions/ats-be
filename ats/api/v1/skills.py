from fastapi import APIRouter, Depends, status, HTTPException
from ats.models.applicant import SkillBase, SkillCreate
from ats.services.applicant_service import ApplicantService
from ats.core.utils import run_in_thread
from ats.security.auth_dependency import get_odoo_env_dependency_async, require_role

router = APIRouter(prefix="/v1/skills", tags=["Skills"])

@router.get(
    "/", 
    response_model=list[SkillBase],
    status_code=status.HTTP_200_OK,
    summary="Get list of available skills"
)
async def list_skills(
    env=Depends(get_odoo_env_dependency_async),
):
    async def _list():
        service = ApplicantService(env)
        return service.list_skills()
    return await run_in_thread(_list)

@router.post(
    "/",
    response_model=SkillBase,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new skill"
)
async def create_skill(
    skill_in: SkillCreate,
    env=Depends(get_odoo_env_dependency_async),
    current_user=Depends(require_role("recruiter", "admin")),
):
    async def _create():
        service = ApplicantService(env)
        return service.create_skill(name=skill_in.name)
    return await run_in_thread(_create)
