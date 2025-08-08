from odoo import models, fields

class ApplicantComment(models.Model):
    _name = "ats.applicant.comment"
    _description = "Internal Comment on Applicant"

    applicant_id = fields.Many2one("ats.applicant.profile", required=True)
    application_id = fields.Many2one("ats.application", required=True)
    author_id = fields.Many2one("res.users", required=True, default=lambda self: self.env.uid)
    comment = fields.Text(required=True)
    created_at = fields.Datetime(default=fields.Datetime.now)