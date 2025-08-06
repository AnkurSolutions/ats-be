from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ApplicantCommentBase(BaseModel):
    applicant_id: int
    application_id: int
    comment: str

    class Config:
        from_attributes = True


class ApplicantCommentCreate(ApplicantCommentBase):
    pass


class ApplicantCommentUpdate(BaseModel):
    comment: Optional[str] = None


class ApplicantCommentResponse(ApplicantCommentBase):
    id: int
    author_id: int
    created_at: datetime
