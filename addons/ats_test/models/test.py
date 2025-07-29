from odoo import models, fields

class AtsTest(models.Model):
    _name = 'ats.test'
    _description = 'Assessment/Test Assigned to Applicant'

    name = fields.Char(required=True)  # Test title
    applicant_id = fields.Many2one('hr.applicant', required=True, ondelete='cascade')
    assigned_at = fields.Datetime(required=True)
    deadline = fields.Datetime()
    submission_url = fields.Char(string="Submission Link")
    score = fields.Float()
    feedback = fields.Text()

    status = fields.Selection([
        ('assigned', 'Assigned'),
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed')
    ], default='assigned', required=True)
