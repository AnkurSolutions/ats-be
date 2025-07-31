# addons/ats_applicant/models/application.py

from odoo import models, fields
from datetime import datetime

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