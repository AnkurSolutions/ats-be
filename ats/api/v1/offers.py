from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ats.models.offer import OfferCreate, OfferUpdate, OfferOut
from ats.services.offer_service import (
    create_offer, list_offers, get_offer_by_id,
    update_offer, delete_offer,
    mark_offer_sent, mark_offer_accepted, mark_offer_rejected
)
from ats.db.session import get_odoo_env_async

router = APIRouter(prefix="/offers", tags=["Offers"])

@router.post("/", response_model=OfferOut)
async def create(payload: OfferCreate):
    async with get_odoo_env_async() as env:
        offer = create_offer(env, payload.dict())
        return offer.read([])[0]

@router.get("/", response_model=list[OfferOut])
async def list(
    applicant_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = 100,
    offset: int = 0
):
    async with get_odoo_env_async() as env:
        offers = list_offers(env, applicant_id, status, limit, offset)
        return offers.read([])

@router.get("/{offer_id}", response_model=OfferOut)
async def get(offer_id: int):
    async with get_odoo_env_async() as env:
        offer = get_offer_by_id(env, offer_id)
        if not offer.exists():
            raise HTTPException(status_code=404, detail="Offer not found")
        return offer.read([])[0]

@router.put("/{offer_id}", response_model=OfferOut)
async def update(offer_id: int, payload: OfferUpdate):
    async with get_odoo_env_async() as env:
        offer = update_offer(env, offer_id, payload.dict(exclude_unset=True))
        if not offer:
            raise HTTPException(status_code=404, detail="Offer not found")
        return offer.read([])[0]

@router.delete("/{offer_id}")
async def delete(offer_id: int):
    async with get_odoo_env_async() as env:
        success = delete_offer(env, offer_id)
        if not success:
            raise HTTPException(status_code=404, detail="Offer not found")
        return {"status": "deleted"}

@router.post("/{offer_id}/send", response_model=OfferOut)
async def send_offer(offer_id: int):
    async with get_odoo_env_async() as env:
        offer = mark_offer_sent(env, offer_id)
        if not offer:
            raise HTTPException(status_code=404, detail="Offer not found")
        return offer.read([])[0]

@router.post("/{offer_id}/accept", response_model=OfferOut)
async def accept_offer(offer_id: int):
    async with get_odoo_env_async() as env:
        offer = mark_offer_accepted(env, offer_id)
        if not offer:
            raise HTTPException(status_code=404, detail="Offer not found")
        return offer.read([])[0]

@router.post("/{offer_id}/reject", response_model=OfferOut)
async def reject_offer(offer_id: int):
    async with get_odoo_env_async() as env:
        offer = mark_offer_rejected(env, offer_id)
        if not offer:
            raise HTTPException(status_code=404, detail="Offer not found")
        return offer.read([])[0]