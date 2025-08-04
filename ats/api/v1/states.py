from fastapi import APIRouter, Depends, HTTPException
from typing import List

from ats.db.session import get_odoo_env_dependency_async
from ats.models.state import StateCreate, StateOut
from ats.security.auth_dependency import require_role
from ats.core.utils import run_in_thread

router = APIRouter(prefix="/v1/states", tags=["States"])

@router.get("/", response_model=List[StateOut])
async def list_states():
    env, cr = await get_odoo_env_dependency_async()
    try:
        states = await run_in_thread(lambda: env["ats.state"].search([]))
        return [StateOut(id=s.id, name=s.name, code=s.code) for s in states]
    finally:
        await run_in_thread(cr.close)

@router.post("/", response_model=StateOut)
async def create_state(state_in: StateCreate, current_user=Depends(require_role("admin", "hr"))):
    env, cr = await get_odoo_env_dependency_async()
    try:
        state = await run_in_thread(lambda: env["ats.state"].create(state_in.model_dump()))
        await run_in_thread(cr.commit)
        return StateOut(id=state.id, name=state.name, code=state.code)
    except Exception as e:
        await run_in_thread(cr.rollback)
        raise HTTPException(400, str(e))
    finally:
        await run_in_thread(cr.close)
