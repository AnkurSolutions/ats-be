from odoo import models, fields, api

class AtsJob(models.Model):
    _name = 'ats.job'
    _description = 'ATS Job Posting'
    _order = 'create_date desc'

    # Basic Info
    name = fields.Char(string="Job Title", required=True)
    description = fields.Html(string="Job Description")

    # Workflow
    status = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('published', 'Published'),
        ('closed', 'Closed'),
        ('archived', 'Archived'),
    ], default='draft', required=True)
    last_status_update_at = fields.Datetime(default=fields.Datetime.now)

    # Linked Models
    created_by = fields.Many2one('res.users', required=True, default=lambda self: self.env.uid)
    hr_job_id = fields.Many2one('hr.job', string="Odoo HR Job", ondelete='set null')
    department_id = fields.Many2one('hr.department', string="Department")
    lga_id = fields.Many2one('ats.lga', string="Location (LGA)")

    # Employment Details
    employment_type = fields.Selection([
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
    ], required=True)

    application_deadline = fields.Date()

    # Salary (Optional)
    salary_min = fields.Float(string="Minimum Salary")
    salary_max = fields.Float(string="Maximum Salary")
    currency_id = fields.Many2one('res.currency', string="Currency")

    # Skills
    required_skill_ids = fields.Many2many(
        'ats.skill',
        'ats_job_ats_skill_rel',
        'job_id',
        'skill_id',
        string="Required Skills",
        ondelete="cascade"
    )

    # Auto-update status timestamp
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