from fastapi import APIRouter, Depends, HTTPException, status
from ats.services.comment_service import CommentService
from ats.models.comment import (
    ApplicantCommentCreate,
    ApplicantCommentResponse
)
from ats.core.utils import run_in_thread, flatten_foreign_keys
from ats.security.auth_dependency import get_odoo_env_dependency_async, require_role

router = APIRouter(prefix="/v1/comments", tags=["Applicant Comments"])

READ_FIELDS = ["id", "application_id", "applicant_id", "author_id", "comment", "created_at"]

# ---- Add New Comment ----
@router.post(
    "/",
    response_model=ApplicantCommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add internal comment to applicant"
)
async def add_comment(
    payload: ApplicantCommentCreate,
    current_user=Depends(require_role("admin", "hr", "recruiter", "panelist")),
):
    env, cr = await get_odoo_env_dependency_async()
    service = CommentService(env)
    try:
        comment = await run_in_thread(
            service.add_comment,
            application_id=payload.application_id,
            applicant_id=payload.applicant_id,
            user_id=current_user["id"],
            comment=payload.comment,
        )
        await run_in_thread(cr.commit)

        comment_data = await run_in_thread(lambda: comment.read(READ_FIELDS)[0])
        flatten_foreign_keys(comment_data, ["application_id", "applicant_id", "author_id"])
        return ApplicantCommentResponse(**comment_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to add comment: {str(e)}")
    finally:
        await run_in_thread(cr.close)

# ---- Get Comments for a Specific Application ----
@router.get(
    "/application/{application_id}",
    response_model=list[ApplicantCommentResponse],
    summary="Get all internal comments for an application"
)
async def get_comments_by_application(
    application_id: int,
    current_user=Depends(require_role("admin", "hr", "recruiter", "panelist")),
):
    env, cr = await get_odoo_env_dependency_async()
    service = CommentService(env)
    try:
        comments = await run_in_thread(service.get_comments_for_application, application_id=application_id)
        comment_data = await run_in_thread(lambda: comments.read(READ_FIELDS))
        for record in comment_data:
            flatten_foreign_keys(record, ["application_id", "applicant_id", "author_id"])
        return [ApplicantCommentResponse(**record) for record in comment_data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve comments: {str(e)}")
    finally:
        await run_in_thread(cr.close)

# ---- Get Comments for a Specific Applicant ----
@router.get(
    "/applicant/{applicant_id}",
    response_model=list[ApplicantCommentResponse],
    summary="Get all internal comments for an applicant"
)
async def get_comments_by_applicant(
    applicant_id: int,
    current_user=Depends(require_role("admin", "hr", "recruiter", "panelist")),
):
    env, cr = await get_odoo_env_dependency_async()
    service = CommentService(env)
    try:
        comments = await run_in_thread(service.get_comments_for_applicant, applicant_id=applicant_id)
        comment_data = await run_in_thread(lambda: comments.read(READ_FIELDS))
        for record in comment_data:
            flatten_foreign_keys(record, ["application_id", "applicant_id", "author_id"])
        return [ApplicantCommentResponse(**record) for record in comment_data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve comments: {str(e)}")
    finally:
        await run_in_thread(cr.close)

# ---- Delete a Comment ----
@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete internal comment"
)
async def delete_comment(
    comment_id: int,
    current_user=Depends(require_role("admin", "hr")),
):
    env, cr = await get_odoo_env_dependency_async()
    service = CommentService(env)
    try:
        deleted = await run_in_thread(service.delete_comment, comment_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Comment not found or already deleted")
        await run_in_thread(cr.commit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete comment: {str(e)}")
    finally:
        await run_in_thread(cr.close)