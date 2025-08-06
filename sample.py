from pydantic import BaseModel, EmailStr, ConfigDict
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

    # Use Pydantic v2 style config (but keeping v1 for compatibility)
    class Config:
        orm_mode = True
        use_enum_values = True  # This ensures enums are serialized as their values

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[UserRole] = None
    
    class Config:
        use_enum_values = True

class UserOut(UserBase):
    id: int
    create_date: datetime

    class Config:
        orm_mode = True
        use_enum_values = True

# Test the model directly
if __name__ == "__main__":
    # Test data
    test_data = {
        "name": "John Doe",
        "email": "john.doe@example.com", 
        "role": "hr",
        "password": "strongpassword123"
    }
    
    try:
        user = UserCreate(**test_data)
        print(f"Success: {user}")
        print(f"Model dump: {user.model_dump()}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()