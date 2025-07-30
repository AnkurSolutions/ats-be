import logging
import asyncio
from fastapi import APIRouter, HTTPException, Depends
from ats.models.user import UserCreate, UserOut, UserUpdate
from ats.services.user_service import (
    create_user, get_user_by_id, resolve_user_role, update_user, delete_user, list_users
)
from ats.db.session import get_odoo_env_dependency_async
from ats.security.auth_dependency import require_role
from concurrent.futures import ThreadPoolExecutor

from odoo.api import Environment

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/users", tags=["Users"])

# Thread pool for running sync Odoo service operations
executor = ThreadPoolExecutor(max_workers=10)

async def get_env_with_cleanup():
    """Helper to get Odoo environment with proper cleanup - Async version"""
    return Depends(get_odoo_env_dependency_async)

async def run_in_thread(func, *args, **kwargs):
    """Helper to run sync functions in thread pool"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, func, *args, **kwargs)

@router.post("/", response_model=UserOut, summary="Create a new user")
async def create_new_user(
    user_data: UserCreate,
    current_user = Depends(require_role("admin", "hr"))  # Only admin
):
    """
    Create a new user in the system.
    
    - **name**: User's full name
    - **email**: User's email address (must be valid email)
    - **role**: User's role (hr, recruiter, interviewer, admin)
    - **password**: User's password
    """
    env, cr = None, None
    try:
        logger.info(f"Creating new user: {user_data.email}")
        
        # Get environment asynchronously
        env, cr = await get_odoo_env_dependency_async()
        
        # Run sync operations in thread pool
        user_dict = user_data.model_dump()
        new_user = await run_in_thread(create_user, env, user_dict)
        
        if not await run_in_thread(new_user.exists):
            raise HTTPException(status_code=500, detail="Failed to create user")
            
        user_record = await run_in_thread(
            lambda: new_user.read(['id', 'name', 'email', 'create_date'])[0]
        )
        user_record['role'] = user_data.role
        
        # Commit and close connection asynchronously
        await run_in_thread(cr.commit)
        await run_in_thread(cr.close)
        
        logger.info(f"Successfully created user with ID: {user_record['id']}")
        return user_record
        
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        # Cleanup on error
        if cr:
            try:
                await run_in_thread(cr.rollback)
                await run_in_thread(cr.close)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

@router.get("/", response_model=list[UserOut], summary="Get all users")
async def get_all_users(
    current_user = Depends(require_role("admin", "hr"))  # Admin and HR
):
    """
    Retrieve all users from the system.
    
    Returns a list of all users with their basic information.
    """
    env, cr = None, None
    try:
        logger.info("Fetching all users")
        
        # Get environment asynchronously
        env, cr = await get_odoo_env_dependency_async()
        
        # Run sync operations in thread pool
        users = await run_in_thread(list_users, env)
        user_records = await run_in_thread(
            lambda: users.read(['id', 'name', 'email', 'create_date'])
        )
        
        # Add role resolution (implement proper role resolution later)
        for record in user_records:
            user = env['res.users'].browse(record['id'])
            record['role'] = resolve_user_role(env, user)

            
        # Commit and close connection asynchronously
        await run_in_thread(cr.commit)
        await run_in_thread(cr.close)
        
        logger.info(f"Retrieved {len(user_records)} users")
        return user_records
        
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        if cr:
            try:
                await run_in_thread(cr.rollback)
                await run_in_thread(cr.close)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")

@router.get("/{user_id}", response_model=UserOut, summary="Get user by ID")
async def get_user_by_id_endpoint(
    user_id: int,
    current_user = Depends(require_role("admin", "hr"))
):
    """
    Retrieve a specific user by their ID.
    
    - **user_id**: The ID of the user to retrieve
    """
    env, cr = None, None
    try:
        logger.info(f"Fetching user with ID: {user_id}")
        
        # Get environment asynchronously  
        env, cr = await get_odoo_env_dependency_async()
        
        # Run sync operations in thread pool
        user = await run_in_thread(get_user_by_id, env, user_id)
        if not await run_in_thread(user.exists):
            raise HTTPException(status_code=404, detail="User not found")
        
        user_record = await run_in_thread(
            lambda: user.read(['id', 'name', 'email', 'create_date'])[0]
        )
        user_record['role'] = resolve_user_role(env, user)
        
        # Commit and close connection asynchronously
        await run_in_thread(cr.commit)
        await run_in_thread(cr.close)
        
        logger.info(f"Successfully retrieved user: {user_record['email']}")
        return user_record
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        if cr:
            try:
                await run_in_thread(cr.close)
            except:
                pass
        raise
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {str(e)}")
        if cr:
            try:
                await run_in_thread(cr.rollback)
                await run_in_thread(cr.close)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")

@router.put("/{user_id}", response_model=UserOut, summary="Update user")
async def update_user_by_id(
    user_id: int,
    user_updates: UserUpdate,
    current_user = Depends(require_role("admin"))  # Only admin
):
    """
    Update a specific user's information.
    
    - **user_id**: The ID of the user to update
    - **name**: New name (optional)
    - **role**: New role (optional)
    """
    env, cr = None, None
    try:
        logger.info(f"Updating user with ID: {user_id}")
        
        # Get environment asynchronously
        env, cr = await get_odoo_env_dependency_async()
        
        # Run sync operations in thread pool
        update_data = user_updates.model_dump(exclude_unset=True)
        updated_user = await run_in_thread(update_user, env, user_id, update_data)
        
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_record = await run_in_thread(
            lambda: updated_user.read(['id', 'name', 'email', 'create_date'])[0]
        )
        user_record['role'] = user_updates.role if user_updates.role else 'hr'
        
        # Commit and close connection asynchronously
        await run_in_thread(cr.commit)
        await run_in_thread(cr.close)
        
        logger.info(f"Successfully updated user: {user_record['email']}")
        return user_record
        
    except HTTPException:
        if cr:
            try:
                await run_in_thread(cr.close)
            except:
                pass
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        if cr:
            try:
                await run_in_thread(cr.rollback)
                await run_in_thread(cr.close)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")

@router.delete("/{user_id}", summary="Delete user")
async def delete_user_by_id(
    user_id: int,
    current_user = Depends(require_role("admin"))  # Only admin
):
    """
    Delete a specific user from the system.
    
    - **user_id**: The ID of the user to delete
    """
    env, cr = None, None
    try:
        logger.info(f"Deleting user with ID: {user_id}")
        
        # Get environment asynchronously
        env, cr = await get_odoo_env_dependency_async()
        
        # Run sync operations in thread pool
        deleted = await run_in_thread(delete_user, env, user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Commit and close connection asynchronously
        await run_in_thread(cr.commit)
        await run_in_thread(cr.close)
        
        logger.info(f"Successfully deleted user with ID: {user_id}")
        return {"message": "User deleted successfully", "user_id": user_id}
        
    except HTTPException:
        if cr:
            try:
                await run_in_thread(cr.close)
            except:
                pass
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        if cr:
            try:
                await run_in_thread(cr.rollback)
                await run_in_thread(cr.close)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")