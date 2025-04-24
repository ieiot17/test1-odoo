from odoo.exceptions import UserError
 
class CJMStateHandler:
    def __init__(self, record, user, crm_user_id, creator_user_id, plan_writer_user_id):
        self.record = record
        self.user = user
        self.crm_user_id = crm_user_id
        self.creator_user_id = creator_user_id
        self.plan_writer_user_id = plan_writer_user_id

    def handle_state_transition(self):
        """ Main entry point for handling state transitions """
        state = self.record.progen_cj_state
        
        if state == 'draft':
            self._handle_draft_state()

        elif state == 'rm_ready':
            self._handle_rm_ready_state()

        elif state == 'submitted':
            self._handle_submitted_state()

        elif state == 'crm_ready':
            self._handle_crm_ready_state()

        else:
            raise UserError("Invalid state for submission.")

    def _handle_draft_state(self):
        """ Handle actions when state is 'draft' """
        if not self.user.has_group('progen.progen_researcher'):
            raise UserError("Only Researchers can submit in Draft state.")
        if not self.record.ready_for_review:
            raise UserError("Record must be marked Ready for Review.")
        
        self.record.write({'progen_cj_state': 'rm_ready', 'ready_for_review': False})
        self._create_activity(self.creator_user_id, "Review Required")

    def _handle_rm_ready_state(self):
        """ Handle actions when state is 'rm_ready' """
        if not self.user.has_group('progen.progen_rm'):
            raise UserError("Only RMs can submit in RM Ready state.")
        
        if self.record.ready_for_review:
            self._process_ready_for_review_state()
        else:
            self._set_draft_state_back()

    def _process_ready_for_review_state(self):
        """ Process when the record is ready for review """
        if self.record.scorecard_total >= 70 and self.record.progen_review_status in ['client_ready', 'revisions_required']:
            self.record.write({'progen_cj_state': 'crm_ready', 'ready_for_review': False})
            self._create_activity(self.crm_user_id, "Review Required")
        else:
            self.record.write({'progen_cj_state': 'submitted', 'ready_for_review': False})
            self._create_activity(self.record.progen_reviewer_id.id, "Review Required")

    def _set_draft_state_back(self):
        """ Reset record back to draft if needed """
        if self.plan_writer_user_id and self.user.id != self.plan_writer_user_id:
            self.record.write({'progen_cj_state': 'draft'})
            self._create_activity(self.plan_writer_user_id, "Draft Status Update")

    def _handle_submitted_state(self):
        """ Handle actions when state is 'submitted' """
        if not self.user.has_group('progen.progen_reviewer'):
            raise UserError("Only Reviewers can submit in Submitted state.")
        if not self.record.progen_review_status:
            raise UserError("Set the Review Status.")

        self.record.write({'ready_for_review': False})
        if self.record.scorecard_total >= 70 and self.record.progen_review_status in ['client_ready', 'revisions_required']:
            self.record.write({'progen_cj_state': 'rm_ready'})
            self._create_activity(self.creator_user_id, "Review Required")
        else:
            self.record.write({'progen_cj_state': 'rm_ready'})
            self._create_activity(self.creator_user_id, "Draft Status Update")

    def _handle_crm_ready_state(self):
        """ Handle actions when state is 'crm_ready' """
        if not self.user.has_group('progen.progen_crm'):
            raise UserError("Only CRM can submit in CRM Ready state.")
        
        if not self.record.ready_for_review:
            self.record.write({'progen_cj_state': 'rm_ready'})
            self._create_activity(self.creator_user_id, "Review Required")
        else:
            self.record.write({'progen_cj_state': 'client_ready', 'ready_for_review': False})
            self._create_activity(self.creator_user_id, "Client Ready")

    def _create_activity(self, user_id, summary):
        """ Helper to create activity """
        activity_type = self.record.env.ref('mail.mail_activity_data_todo').id
        if user_id:
            self.record.activity_schedule(
                activity_type_id=activity_type,
                summary=summary,
                note="Please review this document and provide feedback.",
                user_id=user_id
            )
