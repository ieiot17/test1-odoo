from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError
from .helpers.validator import TimeSheetValidator
from .helpers.notifier import ProjectNotifier

class AnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    start_time = fields.Char(string="Start Time (HHMM)")
    end_time = fields.Char(string="End Time (HHMM)")

    @api.model
    def create(self, vals):
        project = self.env['project.project'].browse(vals.get('project_id'))
        if project and project.closed:
            raise UserError(_("You cannot submit timesheets for closed projects."))

        res = super().create(vals)
        ProjectNotifier(res).notify_if_exceeded()
        return res

    def write(self, vals):
        for record in self:
            project_id = vals.get('project_id', record.project_id.id)
            project = self.env['project.project'].browse(project_id)
            if project and project.closed:
                raise UserError(_("You cannot update timesheets for closed projects."))

        res = super().write(vals)
        for record in self:
            ProjectNotifier(record).notify_if_exceeded()
        return res

    @api.constrains('employee_id', 'date', 'start_time', 'end_time', 'project_id')
    def _check_time_policies(self):
        validator = TimeSheetValidator(self.env, self.env.user)
        for record in self:
            if record.start_time and record.end_time:
                validator.validate(record)
