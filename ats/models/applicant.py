from pydantic import BaseModel, EmailStr, HttpUrl, Field
from typing import List, Optional

# ----- Skill Schemas -----
class SkillBase(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class SkillCreate(BaseModel):
    name: str

# ----- Applicant Profile Schemas -----
# Better model structure
class ApplicantProfileBase(BaseModel):
    resume_url: Optional[str] = None
    skill_ids: Optional[List[int]] = []
    experience_years: int = 0
    status: str = "active"

class ApplicantProfileUpdate(BaseModel):
    resume_url: Optional[str] = Field(None)
    skill_ids: Optional[List[int]] = Field(None)
    experience_years: Optional[int] = Field(None)
    status: Optional[str] = Field(None)

class ApplicantProfileResponse(ApplicantProfileBase):
    id: int
    user_id: int

class ApplicantOnboardRequest(ApplicantProfileBase):
    pass

    class Config:
        from_attributes = True
        use_enum_values = True
