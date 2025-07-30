from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


class JobStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    PUBLISHED = "published"
    CLOSED = "closed"
    ARCHIVED = "archived"  # For auto-archive


class ApprovalStatus(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"


# --- Request Schemas ---

class JobCreate(BaseModel):
    title: str
    description: str = Field(..., description="HTML content")
    # created_by inferred from JWT context

class JobUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]

class JobApproveRequest(BaseModel):
    status: ApprovalStatus
    comment: Optional[str] = None


# --- Response Schemas ---

class JobOut(BaseModel):
    id: int
    title: str
    description: str
    status: JobStatus
    created_by: dict  # Simple user dict
    last_status_update_at: datetime

    class Config:
        from_attributes = True  # Allows Odoo model serialization
        use_enum_values = True


class JobApprovalOut(BaseModel):
    id: int
    job_id: int
    approver_id: int
    status: ApprovalStatus
    comment: Optional[str]
    approved_at: datetime

    class Config:
        from_attributes = True
        use_enum_values = True
