from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    HR = "hr"
    RECRUITER = "recruiter"
    INTERVIEWER = "interviewer"
    ADMIN = "admin"

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: UserRole

    class Config:
        from_attributes = True  # Changed from orm_mode = True
        use_enum_values = True  # Ensures enums serialize as strings

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[UserRole] = None
    
    class Config:
        use_enum_values = True

class UserOut(UserBase):
    id: int
    create_date: datetime  # <-- match the field your ORM returns

    class Config:
        from_attributes = True  # Changed from orm_mode = True
        use_enum_values = True