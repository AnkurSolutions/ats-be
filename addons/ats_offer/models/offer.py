from odoo import models, fields
from datetime import datetime

class AtsOffer(models.Model):
    _name = 'ats.offer'
    _description = 'Job Offer'

    name = fields.Char(required=True)
    applicant_id = fields.Many2one('hr.applicant', required=True, ondelete='cascade')
    position_title = fields.Char()
    salary = fields.Float()
    currency_id = fields.Many2one('res.currency', string='Currency')
    offer_letter_url = fields.Char(string="Offer Letter URL")
    job_id = fields.Many2one('hr.job', string="Job Position")

    status = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ], default='draft', required=True)

    sent_at = fields.Datetime()
    accepted_at = fields.Datetime()
    rejected_at = fields.Datetime()
    notes = fields.Text()

    def action_send(self):
        self.write({'status': 'sent', 'sent_at': fields.Datetime.now()})

    def action_accept(self):
        self.write({
            'status': 'accepted',
            'accepted_at': fields.Datetime.now()
        })

        for offer in self:
            applicant = offer.applicant_id

            # Step 1: Ensure employee exists
            if not applicant.emp_id:
                applicant.create_employee()  # Odoo's built-in method
            employee = applicant.emp_id

            # Step 2: Create contract
            contract_vals = {
                'name': offer.name,
                'employee_id': employee.id,
                'job_id': offer.job_id.id if offer.job_id else False,
                'wage': offer.salary or 0.0,
                'currency_id': offer.currency_id.id,
                'date_start': fields.Date.today(),
                'notes': offer.notes or '',
            }

            self.env['hr.contract'].create(contract_vals)

    def action_reject(self):
        self.write({'status': 'rejected', 'rejected_at': fields.Datetime.now()})
