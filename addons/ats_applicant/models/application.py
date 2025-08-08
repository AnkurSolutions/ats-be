from odoo import models, fields, api, exceptions

class Application(models.Model):
    _name = 'ats.application'
    _description = 'Job Application'
    _order = 'submitted_at desc'

    job_id = fields.Many2one('ats.job', required=True, ondelete='cascade', string="Job")
    applicant_id = fields.Many2one('ats.applicant.profile', required=True, ondelete='cascade', string="Applicant")
    submitted_at = fields.Datetime(string="Submission Date", default=lambda self: fields.Datetime.now())

    status = fields.Selection([
        ('applied', 'Applied'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('offered', 'Offered'),
        ('hired', 'Hired'),
    ], default='applied', string="Application Status")

    current_stage = fields.Selection([
        ('applied', 'Applied'),
        ('shortlisted', 'Shortlisted'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('offered', 'Offered'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
    ], default='applied', string="Current Stage")

    reviewed_at = fields.Datetime(string="Reviewed At")
    reviewed_by = fields.Many2one('res.users', string="Reviewed By")
    decision_notes = fields.Text(string="Decision Notes")

    tag_ids = fields.Many2many("ats.application.tag", string="Tags")
    comment_ids = fields.One2many("ats.applicant.comment", "application_id", string="Internal Comments")
    status_history_ids = fields.One2many("ats.application.status.history", "application_id", string="Status History")
    source = fields.Char(string="Application Source")

    _sql_constraints = [
        ('unique_application', 'unique(job_id, applicant_id)', 'Applicant has already applied to this job.')
    ]

    VALID_TRANSITIONS = {
        'applied': ['shortlisted', 'rejected'],
        'shortlisted': ['interview_scheduled', 'rejected'],
        'interview_scheduled': ['offered', 'rejected'],
        'offered': ['hired', 'rejected'],
    }

    @api.model
    def create(self, vals):
        vals.setdefault("current_stage", vals.get("status", "applied"))
        return super().create(vals)

    def change_status(self, new_status):
        for record in self:
            if new_status not in self.VALID_TRANSITIONS.get(record.status, []):
                raise exceptions.ValidationError(f"Invalid transition from {record.status} to {new_status}")
            record.status = new_status