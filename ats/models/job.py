from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from datetime import date, datetime

class JobStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    PUBLISHED = "published"
    CLOSED = "closed"
    ARCHIVED = "archived"


class ApprovalStatus(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"


class EmploymentType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"

class JobCreate(BaseModel):
    title: str
    description: str = Field(..., description="HTML content")
    department_id: int
    lga_id: int
    employment_type: EmploymentType
    application_deadline: date
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency_id: Optional[int] = None
    required_skill_ids: Optional[List[int]] = []

class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    department_id: Optional[int] = None
    lga_id: Optional[int] = None
    employment_type: Optional[EmploymentType] = None
    application_deadline: Optional[date] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency_id: Optional[int] = None
    required_skill_ids: Optional[List[int]] = None

class JobStatusUpdateRequest(BaseModel):
    status: JobStatus
class JobApproveRequest(BaseModel):
    status: ApprovalStatus
    comment: Optional[str] = None

class UserShortOut(BaseModel):
    id: int
    name: str
    email: Optional[EmailStr] = None

    class Config:
        from_attributes = True


class DepartmentOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class StateOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class LGAOut(BaseModel):
    id: int
    name: str
    state: StateOut

    class Config:
        from_attributes = True


class SkillOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class CurrencyOut(BaseModel):
    id: int
    name: str
    symbol: Optional[str] = None

    class Config:
        from_attributes = True

class JobOut(BaseModel):
    id: int
    title: str
    description: str
    status: JobStatus
    employment_type: EmploymentType
    application_deadline: Optional[date]
    salary_min: Optional[float]
    salary_max: Optional[float]
    currency: Optional[CurrencyOut]
    department: Optional[DepartmentOut]
    location: Optional[LGAOut]
    required_skills: List[SkillOut] = []
    created_by: UserShortOut
    last_status_update_at: datetime

    class Config:
        from_attributes = True
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

