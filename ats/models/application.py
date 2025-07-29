from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class ApplicationBase(BaseModel):
    name: str                      # Applicant name
    email: Optional[EmailStr] = None
    job_id: int                    # Required link to job
    partner_name: Optional[str] = None
    description: Optional[str] = None
    source_id: Optional[int] = None   # Source (LinkedIn, etc.)
    user_id: Optional[int] = None     # Recruiter assigned

class ApplicationCreate(ApplicationBase):
    pass

class ApplicationUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    job_id: Optional[int] = None
    partner_name: Optional[str] = None
    description: Optional[str] = None
    source_id: Optional[int] = None
    user_id: Optional[int] = None

class ApplicationOut(ApplicationBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class PublicApplication(BaseModel):
    name: str
    email: EmailStr
    cover_letter: Optional[str] = None
    resume_url: Optional[str] = None   # stored in `description` for now