from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class ProgenCJM(models.Model):
    _name = 'progen.cjm'
    _description = 'Progen CJM'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id'
    _rec_name = 'name'

    # Fields
    execution = fields.Integer(string="Execution")
    file_upload_rp = fields.Binary(string="Research Plan")
    general_plan_format = fields.Integer(string="General Plan Format")
    name = fields.Char(string="Name")
    progen_cj_description = fields.Text(string="Description")
    progen_cj_notes = fields.Text(string="Notes")
    progen_cj_planwriter = fields.Many2one('res.users', string="Plan Writer", domain="[('groups_id', 'in', [13,12])]")  # 'Researcher' and 'RM' group IDs
    progen_cj_state = fields.Selection([
        ('draft', 'Draft'),
        ('rm_ready', 'RM Ready'),
        ('submitted', 'Reviewer Ready'),
        ('crm_ready', 'CRM Ready'),
        ('client_ready', 'Client Ready')
    ], string="States")
    progen_reviewer_id = fields.Many2one('res.users', string="Reviewer")
    progen_review_status = fields.Selection([
        ('client_ready', 'Client Ready (Minor or No edits) - RESUBMISSION NOT REQUIRED'),
        ('revisions_required', 'Revisions Requested - RESUBMISSION NOT REQUIRED'),
        ('major_revisions_required', 'Major Revisions Required - RESUBMISSION REQUIRED')
    ], string="Review Status")
    ready_for_review = fields.Boolean(string="Ready For Review")
    resource_identified = fields.Integer(string="Resources Identified")
    review_client_info = fields.Integer(string="Review and Incorporation of Client Information")
    scorecard_total = fields.Integer(string="Scorecard Total", compute="_compute_scorecard_total", store=True)

    # Methods

    @api.model
    def create(self, vals):
        """ Logic to set the initial state based on user group """
        user = self.env.user

        if not vals.get('progen_cj_state'):
            if user.has_group('progen.progen_rm'):
                vals['progen_cj_state'] = 'rm_ready'
            elif user.has_group('progen.progen_researcher'):
                vals['progen_cj_state'] = 'draft'
            else:
                _logger.warning("User not in expected groups. State not set.")

        return super(ProgenCJM, self).create(vals)

    @api.depends('general_plan_format', 'review_client_info', 'resource_identified', 'execution')
    def _compute_scorecard_total(self):
        """ Calculate scorecard total """
        for record in self:
            record.scorecard_total = (
                (record.general_plan_format or 0) +
                (record.review_client_info or 0) +
                (record.resource_identified or 0) +
                (record.execution or 0)
            )

    @api.constrains('progen_cj_planwriter')
    def _check_planwriter_group(self):
        """ Ensure planwriter is either a Researcher or RM """
        for rec in self:
            user = rec.progen_cj_planwriter
            if user and not (user.has_group('progen.progen_researcher') or user.has_group('progen.progen_rm')):
                raise ValidationError("Planwriter must be a Researcher or RM.")
    
    @api.onchange('general_plan_format', 'review_client_info', 'resource_identified', 'execution')
    def _onchange_field_limits(self):
        """ Ensure fields do not exceed maximum values """
        limits = {
            'general_plan_format': 20,
            'review_client_info': 30,
            'resource_identified': 20,
            'execution': 30,
        }
        for field, limit in limits.items():
            return self._validate_and_reset_field(field, limit)


    def _validate_and_reset_field(self, field, limit):
        """Validates a field against its limit. Resets value and returns warning if limit exceeded."""
        value = getattr(self, field)
        
        if value and value > limit:
            setattr(self, field, 0)
            field_label = self.fields_get([field])[field]['string'] if field in self.fields_get() else field.replace('_', ' ').title()
            warning_msg = f"{field_label} should not exceed {limit}. It has been reset to 0."
            return {
                'warning': {
                    'title': "Value Exceeded",
                    'message': warning_msg,
                }
            }

    def action_submit_review(self):
        """ Main entry point for submitting review actions """
        user = self.env.user
        crm_employee = self.env['hr.employee'].search([('work_email', '=', 'kkandi.altimetrik@ancestry.com')], limit=1)
        crm_user_id = crm_employee.user_id.id if crm_employee and crm_employee.user_id else False
        creator_user_id = self.create_uid.id if self.create_uid else False
        plan_writer_user_id = self.progen_cj_planwriter.id

        # Using CJMStateHandler to handle state transitions
        from .state_handler import CJMStateHandler
        state_handler = CJMStateHandler(self, user, crm_user_id, creator_user_id, plan_writer_user_id)
        state_handler.handle_state_transition()
