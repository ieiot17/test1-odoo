from odoo import models, fields

class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    project_default_stage = fields.Boolean(string="Default")
