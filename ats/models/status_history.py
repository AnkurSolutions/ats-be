from pydantic import BaseModel
from typing import Literal
from datetime import datetime


StatusType = Literal[
    'applied',
    'shortlisted',
    'rejected',
    'interview_scheduled',
    'offered',
    'hired'
]


class ApplicationStatusHistoryBase(BaseModel):
    application_id: int
    from_status: StatusType
    to_status: StatusType

    class Config:
        from_attributes = True


class ApplicationStatusHistoryCreate(ApplicationStatusHistoryBase):
    pass


class ApplicationStatusHistoryResponse(ApplicationStatusHistoryBase):
    id: int
    changed_by: int
    changed_at: datetime