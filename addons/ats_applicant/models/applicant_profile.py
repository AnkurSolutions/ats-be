from odoo import models, fields

class ApplicantProfile(models.Model):
    _name = 'ats.applicant.profile'
    _description = 'Applicant Profile'

    user_id = fields.Many2one('res.users', required=True, ondelete='cascade', string="User")
    resume_url = fields.Char(string="Resume URL")
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")  # Optional, override res.users.email if needed

    skill_ids = fields.Many2many('ats.skill', string="Skills")
    experience_years = fields.Integer(string="Years of Experience")
    education_summary = fields.Text(string="Education Summary")
    work_summary = fields.Text(string="Work Summary")
    parse_metadata = fields.Json(string="Resume Parse Metadata")

    status = fields.Selection([
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected')
    ], default='active', string="Profile Status")

    stage = fields.Selection([
        ('new', 'New'),
        ('applied', 'Applied'),
        ('shortlisted', 'Shortlisted'),
        ('onboarding', 'Onboarding'),
        ('interview', 'Interview'),
        ('final_interview', 'Final Interview'),
        ('offer', 'Offer'),
        ('hired', 'Hired')
    ], default='shortlisted', string="Application Stage")

    tag_ids = fields.Many2many('ats.application.tag', string="Tags")
    current_location = fields.Char(string="Current Location")
    preferred_job_types = fields.Selection([
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
    ], string="Preferred Job Type")