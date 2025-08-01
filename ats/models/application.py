from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

# ----- Application Schemas -----
class ApplicationBase(BaseModel):
    job_id: int

class ApplicationCreate(ApplicationBase):
    pass

class ApplicationUpdate(BaseModel):
    status: Optional[str] = Field(None, description="Status e.g., applied, shortlisted, rejected")

    @field_validator('status')
    def status_must_be_valid(cls, v):
        allowed = {'applied', 'shortlisted', 'rejected', 'interview_scheduled', 'offered', 'hired'}
        if v is not None and v not in allowed:
            raise ValueError(f'Status must be one of {allowed}')
        return v

class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    applicant_id: int
    submitted_at: datetime
    status: str

    class Config:
        from_attributes = True  # Allows Odoo model serialization
        use_enum_values = True

# ----- Job Search Filter Schema -----
class JobSearchFilters(BaseModel):
    keywords: Optional[str] = Field(None, description="Search keywords")
    location: Optional[str] = Field(None, description="Job location filter")
    job_type: Optional[str] = Field(None, description="Job type filter")