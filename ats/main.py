import odoo
import odoo.tools.config
from fastapi import FastAPI, Depends
from odoo.modules.registry import Registry

import os
from dotenv import load_dotenv

load_dotenv()

# Set your DB config
odoo.tools.config["db_name"] = os.getenv("DB_NAME", "ats_db")
odoo.tools.config["db_host"] = os.getenv("DB_HOST", "localhost")
odoo.tools.config["db_user"] = os.getenv("DB_USER", "odoo_user")
odoo.tools.config["db_password"] = os.getenv("PG_DB_PASSWORD", "odoo_pass")
odoo.tools.config["db_port"] = int(os.getenv("DB_PORT", "5432"))

# Initialize FastAPI app
app = FastAPI(title="ATS API")

# Initialize registry (the ORM environment factory) once at startup
registry = Registry(odoo.tools.config["db_name"])

# Your routers import
from ats.api.v1 import users, jobs, applications, interviews, tests, offers

# Dependency to get a new Odoo env per request
def get_env():
    # env = registry.env(user=USER_ID)
    # You can use user=1 (admin) or dynamic users later
    with registry.cursor() as cr:
        env = odoo.api.Environment(cr, 1, {})
        yield env

# Include your routers with dependency injection
app.include_router(users.router, dependencies=[Depends(get_env)])
app.include_router(jobs.router, dependencies=[Depends(get_env)])
app.include_router(applications.router, dependencies=[Depends(get_env)])
app.include_router(interviews.router, dependencies=[Depends(get_env)])
app.include_router(tests.router, dependencies=[Depends(get_env)])
app.include_router(offers.router, dependencies=[Depends(get_env)])
