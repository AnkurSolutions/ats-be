import odoo
import asyncio
from odoo.modules.registry import Registry
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("DB_NAME", "ats_db")
DEFAULT_UID = 1  # system admin or service user

# Thread pool for running sync Odoo operations
executor = ThreadPoolExecutor(max_workers=10)

@asynccontextmanager
async def get_odoo_env_async(db_name: str = DB_NAME, uid: int = DEFAULT_UID, context: dict = None):
    """Async context manager for Odoo environment"""
    def _create_env():
        registry = Registry(db_name)
        cr = registry.cursor()
        return odoo.api.Environment(cr, uid, context or {}), cr
    
    # Run the sync operation in thread pool
    env, cr = await asyncio.get_event_loop().run_in_executor(executor, _create_env)
    
    try:
        yield env
        # Run commit in thread pool
        await asyncio.get_event_loop().run_in_executor(executor, cr.commit)
    except Exception:
        # Run rollback in thread pool
        await asyncio.get_event_loop().run_in_executor(executor, cr.rollback)
        raise
    finally:
        # Run close in thread pool
        await asyncio.get_event_loop().run_in_executor(executor, cr.close)

async def get_odoo_env_dependency_async():
    """Async FastAPI dependency for Odoo environment"""
    def _create_env():
        registry = Registry(DB_NAME)
        cr = registry.cursor()
        return odoo.api.Environment(cr, DEFAULT_UID, {}), cr
    
    # Run the sync operation in thread pool
    env, cr = await asyncio.get_event_loop().run_in_executor(executor, _create_env)
    return env, cr

# Keep the sync version for compatibility
def get_odoo_env_dependency():
    """Sync FastAPI dependency for Odoo environment"""
    registry = Registry(DB_NAME)
    cr = registry.cursor()
    return odoo.api.Environment(cr, DEFAULT_UID, {})