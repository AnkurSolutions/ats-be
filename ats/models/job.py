from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class JobBase(BaseModel):
    name: str                   # Job title
    description: Optional[str] = None
    requirements: Optional[str] = None
    department_id: Optional[int] = None
    no_of_recruitment: Optional[int] = 1

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    department_id: Optional[int] = None
    no_of_recruitment: Optional[int] = None

class JobOut(JobBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True
