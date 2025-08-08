from odoo import models, fields

class ApplicationStatusHistory(models.Model):
    _name = "ats.application.status.history"
    _description = "Application Status History"

    application_id = fields.Many2one("ats.application", required=True)
    from_status = fields.Selection([
        ('applied', 'Applied'),
        ('shortlisted', 'Shortlisted'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('offered', 'Offered'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
    ], required=True)
    to_status = fields.Selection([
        ('applied', 'Applied'),
        ('shortlisted', 'Shortlisted'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('offered', 'Offered'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
    ], required=True)
    changed_by = fields.Many2one("res.users", required=True, default=lambda self: self.env.uid)
    changed_at = fields.Datetime(default=fields.Datetime.now)
