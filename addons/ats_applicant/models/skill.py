# addons/ats_applicant/models/skill.py

from odoo import models, fields

class Skill(models.Model):
    _name = 'ats.skill'
    _description = 'Applicant Skill'

    name = fields.Char(required=True, unique=True)