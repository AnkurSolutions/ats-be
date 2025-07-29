from odoo import models, fields, api

class AtsInterview(models.Model):
    _name = 'ats.interview'
    _description = 'Interview'

    name = fields.Char(required=True)  # e.g., "First Interview"
    applicant_id = fields.Many2one('hr.applicant', required=True, ondelete='cascade')
    interviewer_id = fields.Many2one('res.users', string="Interviewer")
    scheduled_at = fields.Datetime(required=True)
    location = fields.Char(string="Location / Link")
    feedback = fields.Text()
    rating = fields.Selection(
        [('1', 'Very Poor'), ('2', 'Poor'), ('3', 'Average'), ('4', 'Good'), ('5', 'Excellent')],
        string="Rating"
    )
    status = fields.Selection(
        [('scheduled', 'Scheduled'), ('completed', 'Completed'), ('cancelled', 'Cancelled')],
        default='scheduled',
        required=True
    )
