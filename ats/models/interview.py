from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class InterviewBase(BaseModel):
    name: str
    applicant_id: int
    interviewer_id: Optional[int] = None
    scheduled_at: datetime
    location: Optional[str] = None
    feedback: Optional[str] = None
    rating: Optional[str] = None  # '1'–'5'
    status: Optional[str] = 'scheduled'  # scheduled, completed, cancelled

class InterviewCreate(InterviewBase):
    pass

class InterviewUpdate(BaseModel):
    name: Optional[str] = None
    applicant_id: Optional[int] = None
    interviewer_id: Optional[int] = None
    scheduled_at: Optional[datetime] = None
    location: Optional[str] = None
    feedback: Optional[str] = None
    rating: Optional[str] = None
    status: Optional[str] = None

class InterviewOut(InterviewBase):
    id: int

    class Config:
        orm_mode = True