from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Literal

# ----- Skill Schemas -----
class SkillBase(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class SkillCreate(BaseModel):
    name: str


# ----- Applicant Profile Schemas -----
class ApplicantProfileBase(BaseModel):
    resume_url: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    skill_ids: Optional[List[int]] = []
    experience_years: int = 0
    education_summary: Optional[str] = None
    work_summary: Optional[str] = None
    parse_metadata: Optional[dict] = {}
    current_location: Optional[str] = None
    preferred_job_types: Optional[Literal["full_time", "part_time", "contract", "internship"]] = None
    status: str = "active"
    stage: str = "new"
    tag_ids: Optional[List[int]] = []

    class Config:
        from_attributes = True
        use_enum_values = True


class ApplicantProfileCreate(ApplicantProfileBase):
    user_id: int


class ApplicantProfileUpdate(BaseModel):
    resume_url: Optional[str] = Field(None)
    phone: Optional[str] = Field(None)
    email: Optional[EmailStr] = Field(None)
    skill_ids: Optional[List[int]] = Field(None)
    experience_years: Optional[int] = Field(None)
    education_summary: Optional[str] = Field(None)
    work_summary: Optional[str] = Field(None)
    parse_metadata: Optional[dict] = Field(None)
    current_location: Optional[str] = Field(None)
    preferred_job_types: Optional[Literal["full_time", "part_time", "contract", "internship"]] = Field(None)
    status: Optional[str] = Field(None)
    stage: Optional[str] = Field(None)
    tag_ids: Optional[List[int]] = Field(None)


class ApplicantProfileResponse(ApplicantProfileBase):
    id: int
    user_id: int


class ApplicantOnboardRequest(ApplicantProfileBase):
    user_id: int