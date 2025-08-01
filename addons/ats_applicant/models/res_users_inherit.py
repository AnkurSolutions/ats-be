# addons/ats_applicant/models/res_users_inherit.py

from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    is_applicant = fields.Boolean(string="Is Applicant", default=False)
    applicant_profile_ids = fields.One2many(
        'ats.applicant.profile',
        'user_id',
        string="Applicant Profiles"
    )
