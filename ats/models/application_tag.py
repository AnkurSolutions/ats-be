from pydantic import BaseModel
from typing import Optional


class ApplicationTagBase(BaseModel):
    name: str
    auto_generated: Optional[bool] = False

    class Config:
        from_attributes = True


class ApplicationTagCreate(ApplicationTagBase):
    pass


class ApplicationTagUpdate(BaseModel):
    name: Optional[str] = None
    auto_generated: Optional[bool] = None


class ApplicationTagResponse(ApplicationTagBase):
    id: int