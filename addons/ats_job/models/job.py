from odoo import models, fields, api

class AtsJob(models.Model):
    _name = 'ats.job'
    _description = 'ATS Job Posting'

    name = fields.Char(required=True)
    description = fields.Html()
    status = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('published', 'Published'),
        ('closed', 'Closed'),
        ('archived', 'Archived'),
    ], default='draft')
    created_by = fields.Many2one('res.users', required=True)
    last_status_update_at = fields.Datetime(default=fields.Datetime.now)
    hr_job_id = fields.Many2one('hr.job', string="Odoo HR Job", ondelete='set null')

    _order = 'create_date desc'

    @api.model
    def create(self, vals):
        vals['last_status_update_at'] = fields.Datetime.now()
        return super().create(vals)

    def write(self, vals):
        if 'status' in vals:
            vals['last_status_update_at'] = fields.Datetime.now()
        return super().write(vals)


class AtsJobApproval(models.Model):
    _name = 'ats.job.approval'
    _description = 'ATS Job Approval'

    job_id = fields.Many2one('ats.job', required=True, ondelete='cascade')
    approver_id = fields.Many2one('res.users', required=True)
    status = fields.Selection([
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], required=True)
    comment = fields.Text()
    approved_at = fields.Datetime(default=fields.Datetime.now)
