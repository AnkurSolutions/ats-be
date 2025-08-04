# addons/ats_core/models/ats_lga.py

from odoo import models, fields

class AtsLGA(models.Model):
    _name = 'ats.lga'
    _description = 'Local Government Area'

    name = fields.Char(required=True)
    state_id = fields.Many2one('ats.state', required=True, ondelete='cascade')

    _sql_constraints = [
        ('unique_lga_per_state', 'unique(name, state_id)', 'LGA name must be unique within each state.')
    ]
