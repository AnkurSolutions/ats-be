from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TestBase(BaseModel):
    name: str
    applicant_id: int
    assigned_at: datetime
    deadline: Optional[datetime] = None
    submission_url: Optional[str] = None
    score: Optional[float] = None
    feedback: Optional[str] = None
    status: Optional[str] = 'assigned'

class TestCreate(TestBase):
    pass

class TestUpdate(BaseModel):
    name: Optional[str] = None
    applicant_id: Optional[int] = None
    assigned_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    submission_url: Optional[str] = None
    score: Optional[float] = None
    feedback: Optional[str] = None
    status: Optional[str] = None

class TestOut(TestBase):
    id: int

    class Config:
        orm_mode = True