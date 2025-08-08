from odoo import models, fields

class ApplicationTag(models.Model):
    _name = "ats.application.tag"
    _description = "Application Tag"

    name = fields.Char(required=True)
    auto_generated = fields.Boolean(default=False)
