from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class OfferBase(BaseModel):
    name: str
    applicant_id: int
    position_title: Optional[str] = None
    salary: Optional[float] = None
    currency_id: Optional[int] = None
    offer_letter_url: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = "draft"

class OfferCreate(OfferBase):
    pass

class OfferUpdate(BaseModel):
    name: Optional[str] = None
    applicant_id: Optional[int] = None
    position_title: Optional[str] = None
    salary: Optional[float] = None
    currency_id: Optional[int] = None
    offer_letter_url: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None

class OfferOut(OfferBase):
    id: int
    sent_at: Optional[datetime]
    accepted_at: Optional[datetime]
    rejected_at: Optional[datetime]

    class Config:
        orm_mode = True