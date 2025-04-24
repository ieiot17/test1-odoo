from odoo.exceptions import UserError, ValidationError
from odoo import _
from . import time_utils

class TimeSheetValidator:
    def __init__(self, env, user):
        self.env = env
        self.user = user

    def validate(self, record):
        start_dt = time_utils.parse_hhmm_time(record.start_time, "Start")
        end_dt = time_utils.parse_hhmm_time(record.end_time, "End")
        if start_dt >= end_dt:
            raise ValidationError(_("Start time must be earlier than end time."))

        self._check_overlap(record, start_dt, end_dt)
        self._check_total_hours(record, start_dt, end_dt)
        self._check_date_permissions(record)

        record.unit_amount = time_utils.calculate_duration(start_dt, end_dt)

    def _check_overlap(self, record, start_dt, end_dt):
        existing = self.env['account.analytic.line'].search([
            ('id', '!=', record.id),
            ('employee_id', '=', record.employee_id.id),
            ('date', '=', record.date),
        ])
        for line in existing:
            if not line.start_time or not line.end_time:
                continue
            start_existing = time_utils.parse_hhmm_time(line.start_time)
            end_existing = time_utils.parse_hhmm_time(line.end_time)
            if time_utils.is_overlap(start_dt, end_dt, start_existing, end_existing):
                raise ValidationError(
                    _("Overlapping timesheet on %(date)s: Start: %(start)s | End: %(end)s") % {
                        'date': line.date,
                        'start': line.start_time,
                        'end': line.end_time,
                    }
                )

    def _check_total_hours(self, record, start_dt, end_dt):
        timesheets = self.env['account.analytic.line'].search([
            ('id', '!=', record.id),
            ('employee_id', '=', record.employee_id.id),
            ('project_id', '=', record.project_id.id),
        ])
        total_logged = sum(timesheets.mapped('unit_amount'))
        duration = time_utils.calculate_duration(start_dt, end_dt)
        total_after = total_logged + duration

        if total_after > 2.0 and not record.employee_id.user_id.has_group('base.group_erp_manager'):
            raise ValidationError(_("Cannot log more than 2 hours without manager permission. Total: %.2f") % total_after)

    def _check_date_permissions(self, record):
        group_yesterday_today = self.env.ref('progen.progen_crm').id
        group_last_month_today = self.env.ref('base.group_erp_manager').id
        user_groups = self.user.groups_id.mapped('id')

        today = time_utils.get_today()
        yesterday = time_utils.get_yesterday()
        thirty_days_ago = time_utils.get_thirty_days_ago()

        if group_yesterday_today in user_groups:
            if record.date not in [today, yesterday]:
                raise UserError(_("You can only select today or yesterday."))
        elif group_last_month_today in user_groups:
            if not (thirty_days_ago <= record.date <= today):
                raise UserError(_("You can only select dates from %s to today.") % thirty_days_ago)
        else:
            raise UserError(_("You do not have permission to modify this date."))
