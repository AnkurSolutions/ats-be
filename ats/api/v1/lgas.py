from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from ats.db.session import get_odoo_env_dependency_async
from ats.models.lga import LgaCreate, LgaOut
from ats.security.auth_dependency import require_role
from ats.core.utils import run_in_thread

router = APIRouter(prefix="/v1/lgas", tags=["LGAs"])

@router.get("/", response_model=List[LgaOut])
async def list_lgas(state_id: Optional[int] = Query(None)):
    env, cr = await get_odoo_env_dependency_async()
    try:
        domain = [("state_id", "=", state_id)] if state_id else []
        lgas = await run_in_thread(lambda: env["ats.lga"].search(domain))
        return [LgaOut(id=lga.id, name=lga.name, state_id=lga.state_id.id) for lga in lgas]
    finally:
        await run_in_thread(cr.close)

@router.post("/", response_model=LgaOut)
async def create_lga(lga_in: LgaCreate, current_user=Depends(require_role("admin", "hr"))):
    env, cr = await get_odoo_env_dependency_async()
    try:
        lga = await run_in_thread(lambda: env["ats.lga"].create(lga_in.model_dump()))
        await run_in_thread(cr.commit)
        return LgaOut(id=lga.id, name=lga.name, state_id=lga.state_id.id)
    except Exception as e:
        await run_in_thread(cr.rollback)
        raise HTTPException(400, str(e))
    finally:
        await run_in_thread(cr.close)
