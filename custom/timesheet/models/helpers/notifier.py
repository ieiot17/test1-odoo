from odoo import _
import logging

_logger = logging.getLogger(__name__)

class ProjectNotifier:
    def __init__(self, record):
        self.record = record

    def notify_if_exceeded(self):
        project = self.record.project_id
        if not project or project.allocated_hours <= 0:
            return

        total_logged = sum(project.timesheet_ids.mapped('unit_amount'))
        if total_logged > project.allocated_hours:
            manager = project.user_id.partner_id
            if not manager:
                _logger.warning("No manager set for project: %s", project.name)
                return

            message = _(
                "⚠ The total logged hours (%.2f) exceeded allocated (%.2f) for project '%s'. Notifying: %s"
            ) % (
                total_logged,
                project.allocated_hours,
                project.name,
                manager.name,
            )

            project.message_post(
                body=message,
                partner_ids=[manager.id],
                message_type='comment',
                subtype_xmlid='mail.mt_note',
            )
