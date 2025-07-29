from fastapi import APIRouter, HTTPException, Query
from ats.models.test import TestCreate, TestUpdate, TestOut
from ats.services.test_service import (
    get_test_by_id, list_tests, create_test, update_test, delete_test
)
from ats.db.session import get_odoo_env_async
from typing import Optional

router = APIRouter(prefix="/tests", tags=["Tests"])

@router.post("/", response_model=TestOut)
async def assign_test(payload: TestCreate):
    async with get_odoo_env_async() as env:
        test = create_test(env, payload.dict())
        return test.read([
            'id', 'name', 'applicant_id', 'assigned_at', 'deadline',
            'submission_url', 'status', 'score', 'feedback'
        ])[0]

@router.get("/", response_model=list[TestOut])
async def get_tests(
    applicant_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100),
    offset: int = Query(0)
):
    async with get_odoo_env_async() as env:
        tests = list_tests(env, applicant_id=applicant_id, status=status, limit=limit, offset=offset)
        return tests.read([
            'id', 'name', 'applicant_id', 'assigned_at', 'deadline',
            'submission_url', 'status', 'score', 'feedback'
        ])

@router.get("/{test_id}", response_model=TestOut)
async def get_test(test_id: int):
    async with get_odoo_env_async() as env:
        test = get_test_by_id(env, test_id)
        if not test.exists():
            raise HTTPException(status_code=404, detail="Test not found")
        return test.read([
            'id', 'name', 'applicant_id', 'assigned_at', 'deadline',
            'submission_url', 'status', 'score', 'feedback'
        ])[0]

@router.put("/{test_id}", response_model=TestOut)
async def update_test_api(test_id: int, payload: TestUpdate):
    async with get_odoo_env_async() as env:
        updated = update_test(env, test_id, payload.dict(exclude_unset=True))
        if not updated:
            raise HTTPException(status_code=404, detail="Test not found")
        return updated.read([
            'id', 'name', 'applicant_id', 'assigned_at', 'deadline',
            'submission_url', 'status', 'score', 'feedback'
        ])[0]

@router.delete("/{test_id}")
async def delete_test_api(test_id: int):
    async with get_odoo_env_async() as env:
        deleted = delete_test(env, test_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Test not found")
        return {"status": "deleted"}