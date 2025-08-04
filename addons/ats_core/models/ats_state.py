# addons/ats_core/models/ats_state.py

from odoo import models, fields

class AtsState(models.Model):
    _name = 'ats.state'
    _description = 'Nigerian State'

    name = fields.Char(required=True)
    code = fields.Char()

    _sql_constraints = [
        ('unique_state_name', 'unique(name)', 'State name must be unique.'),
        ('unique_state_code', 'unique(code)', 'State code must be unique.')
    ]
