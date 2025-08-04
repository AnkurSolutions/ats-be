from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel

from ats.db.session import get_odoo_env_dependency_async
from ats.security.auth_dependency import require_role
from ats.core.utils import run_in_thread

router = APIRouter(prefix="/v1/departments", tags=["Departments"])

class DepartmentCreate(BaseModel):
    name: str

class DepartmentOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

@router.get("/", response_model=List[DepartmentOut])
async def list_departments(current_user=Depends(require_role("admin", "hr"))):
    env, cr = await get_odoo_env_dependency_async()
    try:
        departments = await run_in_thread(lambda: env["hr.department"].search([]))
        return [DepartmentOut.model_validate(dept, from_attributes=True) for dept in departments]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await run_in_thread(cr.close)

@router.post("/", response_model=DepartmentOut)
async def create_department(dept: DepartmentCreate, current_user=Depends(require_role("admin"))):
    env, cr = await get_odoo_env_dependency_async()
    try:
        department = await run_in_thread(lambda: env["hr.department"].create({"name": dept.name}))
        await run_in_thread(cr.commit)
        return DepartmentOut.model_validate(department, from_attributes=True)
    except Exception as e:
        await run_in_thread(cr.rollback)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await run_in_thread(cr.close)
