from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional

# ----- Skill Schemas -----
class SkillBase(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class SkillCreate(BaseModel):
    name: str

# ----- Applicant Profile Schemas -----
class ApplicantProfileBase(BaseModel):
    resume_url: Optional[HttpUrl] = Field(None, description="URL to resume")
    skill_ids: Optional[List[int]] = Field(default_factory=list, description="Skill IDs")
    experience_years: Optional[int] = Field(0, ge=0, description="Years of experience")
    status: Optional[str] = Field("active", description="Profile status")

class ApplicantProfileCreate(ApplicantProfileBase):
    pass

class ApplicantProfileUpdate(ApplicantProfileBase):
    status: Optional[str] = Field(None)

class ApplicantProfileResponse(ApplicantProfileBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
        use_enum_values = True
