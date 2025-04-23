from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProjectTask(models.Model):
    _inherit = 'project.task'
    _description = 'Project Task with Budget Management'

    
    task_budget = fields.Float(
        string="Task Budget",
        compute='_compute_task_budget',
        store=True,
        digits=(16, 2),
        help="Calculated budget for this task based on project budget and allocated hours"
    )

    task_remaining_budget = fields.Float(
        string="Task Remaining Budget",
        compute='_compute_task_remaining_budget',
        store=True,
        digits=(16, 2),
        help="Remaining budget based on consumed hours"
    )

    task_timesheet = fields.Boolean(
        string="Task Timesheet",
        compute='_compute_task_timesheet',
        store=True,
        help="Indicates if all allocated hours have been logged in timesheets"
    )

    @api.depends('allocated_hours', 'project_id.session_budget', 'project_id.allocated_hours')
    def _compute_task_budget(self):
        for record in self:
            try:
                if (record.project_id and record.project_id.session_budget and 
                    record.project_id.allocated_hours and record.allocated_hours):
                    record.task_budget = (
                        record.project_id.session_budget / 
                        record.project_id.allocated_hours
                    ) * record.allocated_hours
                else:
                    record.task_budget = 0
            except ZeroDivisionError:
                record.task_budget = 0

    @api.depends('task_budget', 'allocated_hours', 'effective_hours')
    def _compute_task_remaining_budget(self):
        for record in self:
            try:
                if record.allocated_hours:
                    cost_per_hour = record.task_budget / record.allocated_hours
                    record.task_remaining_budget = record.task_budget - (
                        record.effective_hours * cost_per_hour
                    )
                else:
                    record.task_remaining_budget = record.task_budget
            except ZeroDivisionError:
                record.task_remaining_budget = record.task_budget

    @api.depends('remaining_hours')
    def _compute_task_timesheet(self):
        for record in self:
            record.task_timesheet = record.remaining_hours == 0

    @api.constrains('allocated_hours')
    def _check_allocated_hours(self):
        for record in self:
            if record.allocated_hours < 0:
                raise ValidationError("Allocated hours cannot be negative")

    @api.onchange('allocated_hours')
    def _onchange_allocated_hours(self):
        if self.allocated_hours <= 0:
            return {
                'warning': {
                    'title': "Warning",
                    'message': "Allocated hours should be greater than zero"
                }
            }