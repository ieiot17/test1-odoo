from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError
from unittest.mock import patch


class TestProgenCJM(TransactionCase):
    def setUp(self):
        super().setUp()
        self.rm_user = self.env['res.users'].create({
            'name': 'RM User',
            'login': 'rm_user',
            'groups_id': [(6, 0, [self.ref('progen.progen_rm')])],
        })
        self.researcher_user = self.env['res.users'].create({
            'name': 'Researcher User',
            'login': 'researcher_user',
            'groups_id': [(6, 0, [self.ref('progen.progen_researcher')])],
        })
        self.other_user = self.env['res.users'].create({
            'name': 'Other User',
            'login': 'other_user',
        })
        self.ClientJourney = self.env['progen.cjm']

    def change_user(self, user):
        return self.env(user=user)

    def test_create_cjsession_for_rm(self):
        env = self.change_user(self.rm_user)
        ClientJourney = env['progen.cjm']
        cjm = ClientJourney.create({'name': 'Test Session'})
        self.assertEqual(cjm.progen_cj_state, 'rm_ready')

    def test_create_cjsession_for_researcher(self):
        env = self.change_user(self.researcher_user)
        ClientJourney = env['progen.cjm']
        cjm = ClientJourney.create({'name': 'Test Session'})
        self.assertEqual(cjm.progen_cj_state, 'draft')

    @patch('custom.progen_client_journey.models.progen_cjm._logger')
    def test_logging_and_state_set_for_other_user(self, mock_logger):
        env = self.change_user(self.other_user)
        ClientJourney = env['progen.cjm']
        cjm = ClientJourney.create({'name': 'Other User Session'})
        self.assertFalse(cjm.progen_cj_state)  # State should not be set
        mock_logger.warning.assert_called_once()

    def test_planwriter_group_constraint(self):
        with self.assertRaises(ValidationError):
            self.ClientJourney.create({
                'name': 'Invalid Planwriter',
                'progen_cj_planwriter': self.other_user.id
            })

    def test_scorecard_total_computation(self):
        cjm = self.ClientJourney.create({
            'name': 'Scorecard Test',
            'general_plan_format': 10,
            'review_client_info': 10,
            'resource_identified': 5,
            'execution': 5
        })
        cjm._compute_scorecard_total()
        self.assertEqual(cjm.scorecard_total, 30)

    def test_field_limit_onchange_resets_value(self):
        # Field execution exceeds the max limit of 30
        cjm = self.ClientJourney.new({'execution': 35})
        result = cjm._onchange_field_limits()
        self.assertEqual(cjm.execution, 0)
        self.assertIn("has been reset to 0", result['warning']['message'])
