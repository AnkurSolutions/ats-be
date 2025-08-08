from odoo.api import Environment
from datetime import datetime


class CommentService:
    def __init__(self, env: Environment):
        self.env = env
        self.AtsApplicantComment = env['ats.applicant.comment']
        self.AtsApplication = env['ats.application']

    def add_comment(self, *, application_id: int, applicant_id: int, user_id: int, comment: str):
        if not comment.strip():
            raise ValueError("Comment must not be empty.")

        try:
            return self.AtsApplicantComment.create({
                'application_id': application_id,
                'applicant_id': applicant_id,
                'comment': comment,
                'author_id': user_id,
                'created_at': datetime.now()
            })
        except Exception as e:
            raise ValueError(f"Failed to add comment: {str(e)}")

    def get_comments_for_application(self, application_id: int):
        try:
            return self.AtsApplicantComment.search([
                ('application_id', '=', application_id)
            ], order='created_at asc')
        except Exception as e:
            raise ValueError(f"Failed to fetch comments: {str(e)}")

    def get_comments_for_applicant(self, applicant_id: int):
        try:
            return self.AtsApplicantComment.search([
                ('applicant_id', '=', applicant_id)
            ], order='created_at asc')
        except Exception as e:
            raise ValueError(f"Failed to fetch comments: {str(e)}")

    def delete_comment(self, comment_id: int):
        comment = self.AtsApplicantComment.browse(comment_id)
        if not comment.exists():
            return False
        try:
            comment.unlink()
            return True
        except Exception as e:
            raise ValueError(f"Failed to delete comment: {str(e)}")