from odoo import models, fields

class HREmployee(models.Model):
    _inherit = 'hr.employee'

    cost_center_code = fields.Selection([
        ('0', '0 - Unknown'),
        ('153', '153 - Case Manager (Salaried Employee)'),
        ('165', '165 - Assistants (Hourly Employee)'),
    ], string="Cost Center Code")

    progen_employee_type = fields.Many2one('hr.employee.type', string="Employee Type") 

    end_date = fields.Date(string="End Date")
    start_date = fields.Date(string="Start Date")

    exempt = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="Exempt")

    status_board = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="Status Board")

    user_active = fields.Boolean(string="Active", default=True)

    wk_progen_hrs = fields.Float(string="Working Progen Hrs")
