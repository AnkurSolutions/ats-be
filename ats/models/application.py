from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional, List, Literal
from datetime import datetime, date

from ats.models.applicant import ApplicantProfileResponse
from ats.models.job import JobOut
from ats.models.user import UserOut

# ----- Enums -----
StatusType = Literal[
    'applied',
    'shortlisted',
    'rejected',
    'interview_scheduled',
    'offered',
    'hired'
]

#--User Short Out
class UserShortOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True  # Changed from orm_mode = True
        use_enum_values = True  # Ensures enums serialize as strings


# ----- Tags -----
class TagBase(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class TagCreate(BaseModel):
    name: str


class ApplicationTagUpdate(BaseModel):
    tag_ids: List[int] = Field(..., description="List of tag IDs to set on application")


# ----- Comments -----
class ApplicantComment(BaseModel):
    id: int
    body: str
    created_at: datetime
    created_by: Optional[UserOut] = None

    class Config:
        from_attributes = True


# ----- Status History -----
class ApplicationStatusHistory(BaseModel):
    id: int
    application_id: int
    from_status: StatusType
    to_status: StatusType
    changed_by: UserShortOut
    changed_at: datetime

    @field_validator('application_id', mode='before')
    @classmethod
    def validate_application_id(cls, v):
        if isinstance(v, tuple):
            return v[0]  # Return just the ID
        return v

    @field_validator('changed_by', mode='before')
    @classmethod
    def validate_changed_by(cls, v):
        if isinstance(v, tuple):
            user_id, user_name = v
            # Create a minimal UserOut object
            # You'll need to adjust this based on your UserOut model structure
            return {
                'id': user_id,
                'name': user_name,
                # Add other required fields for UserOut
            }
        return v

    class Config:
        from_attributes = True


class ApplicationStatusHistoryCreate(BaseModel):
    application_id: int
    from_status: StatusType
    to_status: StatusType
    changed_by: Optional[int] = None  # Set by service

    # changed_at is handled by Odoo

# ----- Application Create / Update -----
class ApplicationBase(BaseModel):
    job_id: int
    applicant_id: int
    status: Optional[StatusType] = 'applied'
    current_stage: Optional[StatusType] = 'applied'
    source: Optional[str] = None
    decision_notes: Optional[str] = None
    tag_ids: Optional[List[int]] = []

    class Config:
        from_attributes = True
        use_enum_values = True


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    status: Optional[StatusType] = Field(None, description="e.g., shortlisted, rejected")
    current_stage: Optional[StatusType] = Field(None, description="e.g., interview_scheduled")
    decision_notes: Optional[str] = None
    tag_ids: Optional[List[int]] = Field(None)

    @field_validator('status')
    def validate_status(cls, v):
        allowed = {'applied', 'shortlisted', 'rejected', 'interview_scheduled', 'offered', 'hired'}
        if v is not None and v not in allowed:
            raise ValueError(f'Status must be one of {allowed}')
        return v


# ----- Final Response -----
class ApplicationResponse(BaseModel):
    id: int
    job: JobOut
    applicant: ApplicantProfileResponse
    submitted_at: datetime
    status: StatusType
    current_stage: StatusType
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[UserOut] = None
    decision_notes: Optional[str] = None
    source: Optional[str] = None
    tags: List[TagBase] = []
    comment_ids: Optional[List[ApplicantComment]] = []
    status_history_ids: Optional[List[ApplicationStatusHistory]] = []

    class Config:
        from_attributes = True
        use_enum_values = True


# ----- Bulk Update -----
class BulkStatusUpdateRequest(BaseModel):
    application_ids: List[int] = Field(..., description="List of application IDs to update")
    status: StatusType = Field(..., description="New status to apply")


# ----- Job Search Filter Schema -----
class JobSearchFilters(BaseModel):
    keywords: Optional[str] = Field(None, description="Search keywords")
    location: Optional[str] = Field(None, description="Job location filter")
    job_type: Optional[str] = Field(None, description="Job type filter")