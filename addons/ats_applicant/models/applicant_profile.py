# addons/ats_applicant/models/applicant_profile.py

from odoo import models, fields

class ApplicantProfile(models.Model):
    _name = 'ats.applicant.profile'
    _description = 'Applicant Profile'

    user_id = fields.Many2one('res.users', required=True, ondelete='cascade', string="User")
    resume_url = fields.Char(string="Resume URL")
    skill_ids = fields.Many2many('ats.skill', string="Skills")
    experience_years = fields.Integer(string="Years of Experience")
    status = fields.Selection([
        ('active', 'Active'),
        ('archived', 'Archived'),
    ], default='active', string="Profile Status")