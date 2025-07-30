import logging
import os
from fastapi import HTTPException
from odoo.api import Environment
from odoo.exceptions import AccessDenied
from ats.security.jwt_utils import create_access_token
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def get_user_agent_env():
    """
    Get user agent environment from environment variables with sensible defaults.
    """
    return {
        'HTTP_USER_AGENT': os.getenv('ATS_USER_AGENT', 'ATS-FastAPI-Service'),
        'REMOTE_ADDR': os.getenv('ATS_REMOTE_ADDR', '127.0.0.1'),
        'HTTP_X_FORWARDED_FOR': os.getenv('ATS_FORWARDED_FOR', ''),
        'HTTP_HOST': os.getenv('ATS_HTTP_HOST', 'localhost'),
        'SERVER_NAME': os.getenv('ATS_SERVER_NAME', 'ats-api'),
        'REQUEST_METHOD': 'POST',
    }

def authenticate_user(env: Environment, email: str, password: str, request_info: dict = None) -> str:
    logger.info(f"Database: {env.cr.dbname}")
    logger.info(f"Attempting authentication for email: {email}")

    credentials = {
        "login": email,
        "password": password.strip(),
        "type": "password"
    }

    user_agent_env = get_user_agent_env()
    if request_info:
        user_agent_env.update({
            'HTTP_USER_AGENT': request_info.get('user_agent', user_agent_env['HTTP_USER_AGENT']),
            'REMOTE_ADDR': request_info.get('remote_addr', user_agent_env['REMOTE_ADDR']),
            'HTTP_X_FORWARDED_FOR': request_info.get('forwarded_for', ''),
            'HTTP_HOST': request_info.get('host', user_agent_env['HTTP_HOST']),
        })

    try:
        # _login now returns a dict, not just uid
        auth_info = env['res.users'].sudo()._login(env.cr.dbname, credentials, user_agent_env)
        uid = auth_info.get("uid")

        if not uid:
            logger.error("No UID returned from _login")
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user = env['res.users'].sudo().browse(uid)
        if not user or not user.exists():
            logger.error(f"User with ID {uid} not found after login")
            raise HTTPException(status_code=401, detail="Invalid credentials")

        logger.info(f"User found: {user.login}, ID: {user.id}, Name: {user.name}")

        token_data = {
            "sub": str(user.id),
            "email": user.login
        }

        logger.info(f"Authentication successful for {email}, generating JWT")
        return create_access_token(token_data)

    except AccessDenied:
        logger.warning(f"Access denied for email: {email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    except Exception as e:
        logger.error(f"Authentication error for {email}: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid credentials")