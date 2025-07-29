from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ats.security.jwt_utils import decode_access_token
from ats.db.session import get_odoo_env_dependency_async
from ats.services.user_service import resolve_user_role
from odoo.api import Environment
import asyncio

# Security scheme: extracts "Authorization: Bearer <token>"
bearer_scheme = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = int(payload.get("sub"))

    env, cr = await get_odoo_env_dependency_async()
    loop = asyncio.get_event_loop()

    try:
        user = await loop.run_in_executor(None, lambda: env["res.users"].browse(user_id))
        if not await loop.run_in_executor(None, user.exists):
            raise HTTPException(status_code=401, detail="User not found")

        role = await loop.run_in_executor(None, lambda: resolve_user_role(env, user))

        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": role
        }

    except Exception:
        await loop.run_in_executor(None, cr.rollback)
        raise HTTPException(status_code=500, detail="Failed to load user")

    finally:
        await loop.run_in_executor(None, cr.close)

from fastapi import Depends, HTTPException

def require_role(*allowed_roles: str):
    def _guard(current_user = Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Access denied")
        return current_user
    return _guard