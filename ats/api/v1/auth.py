import logging
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr
from ats.core.utils import run_in_thread
from ats.services.auth_service import authenticate_user
from ats.db.session import get_odoo_env_dependency_async
from ats.models.user import UserCreate, UserOut
from ats.services.user_service import create_user
import asyncio

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, request: Request):
    env, cr = await get_odoo_env_dependency_async()
    
    # Extract real request information for production
    logger.info(f"Login attempt for {data.email} from {request.client.host}")
    request_info = {
        'user_agent': request.headers.get('user-agent', 'Unknown'),
        'remote_addr': request.client.host if request.client else '127.0.0.1',
        'forwarded_for': request.headers.get('x-forwarded-for', ''),
        'host': request.headers.get('host', 'localhost'),
    }
    
    try:
        loop = asyncio.get_event_loop()
        token = await loop.run_in_executor(
            None, 
            authenticate_user, 
            env, 
            data.email, 
            data.password, 
            request_info
        )
        await loop.run_in_executor(None, cr.commit)
        logger.info(f"User {data.email} authenticated successfully from {request_info['remote_addr']}")
        return TokenResponse(access_token=token)
    except HTTPException as e:
        logger.error(f"Authentication error for {data.email}: {str(e.detail)}")
        await loop.run_in_executor(None, cr.rollback)
        raise e
    except Exception as e:
        logger.error(f"Authentication error for {data.email}: {str(e)}")
        await loop.run_in_executor(None, cr.rollback)
        raise HTTPException(status_code=500, detail=f"Internal server error")
    finally:
        await loop.run_in_executor(None, cr.close)

@router.post("/register", response_model=UserOut)
async def register_user(data: UserCreate):
    """
    Create a new user in the system.
    
    - **name**: User's full name
    - **email**: User's email address (must be valid email)
    - **role**: User's role (hr, recruiter, interviewer, admin)
    - **password**: User's password
    """
    env, cr = None, None
    try:
        logger.info(f"Creating new user: {data.email}")
        
        # Get environment asynchronously
        env, cr = await get_odoo_env_dependency_async()
        
        # Run sync operations in thread pool
        user_dict = data.model_dump()
        new_user = await run_in_thread(create_user, env, user_dict)
        
        if not await run_in_thread(new_user.exists):
            raise HTTPException(status_code=500, detail="Failed to create user")
            
        user_record = await run_in_thread(
            lambda: new_user.read(['id', 'name', 'email', 'create_date'])[0]
        )
        user_record['role'] = data.role
        
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