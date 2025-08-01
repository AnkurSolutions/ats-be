from fastapi import APIRouter, Depends, status, HTTPException
from ats.models.applicant import SkillBase, SkillCreate
from ats.models.user import UserOut
from ats.services.applicant_service import ApplicantService
from ats.core.utils import run_in_thread
from ats.security.auth_dependency import get_odoo_env_dependency_async, require_role

router = APIRouter(prefix="/v1/skills", tags=["Skills"])

@router.get(
    "/",
    response_model=list[SkillBase],
    status_code=status.HTTP_200_OK,
    summary="List all available skills"
)
async def list_skills(
    current_user: UserOut = Depends(require_role("applicant", "recruiter", "admin")),
):
    env, cr = await get_odoo_env_dependency_async()
    service = ApplicantService(env)
    skills = await run_in_thread(service.list_skills)
    skill_data = await run_in_thread(skills.read, ['id', 'name'])
    await run_in_thread(cr.close)
    return skill_data

@router.post(
    "/",
    response_model=SkillBase,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new skill (if it doesn't exist)"
)
async def create_skill(
    payload: SkillCreate,
    current_user: UserOut = Depends(require_role("applicant", "recruiter", "admin")),
):
    env, cr = await get_odoo_env_dependency_async()
    service = ApplicantService(env)
    skill = await run_in_thread(service.create_skill, name=payload.name)
    skill_data_list = await run_in_thread(skill.read, ['id', 'name'])
    skill_data = skill_data_list[0]
    await run_in_thread(cr.commit)
    await run_in_thread(cr.close)
    return skill_data
