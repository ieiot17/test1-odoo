'''from odoo.tests import common

class TestProjectProjectExtension(common.TransactionCase):

    def setUp(self):
        super().setUp()
        self.Project = self.env['project.project']
        self.Stage = self.env['project.task.type']

        # Create a default task stage
        self.default_stage = self.Stage.create({
            'name': 'Default Stage',
            'project_default_stage': True,
        })

    def test_session_budget_computation(self):
        project = self.Project.create({
            'name': 'Test Budget Project',
            'allocated_hours': 10.0,
            'session_rate': 100.0,
        })
        self.assertAlmostEqual(project.session_budget, 1000.0, places=2)

    def test_session_budget_zero_when_missing_data(self):
        project = self.Project.create({
            'name': 'Incomplete Budget Project',
            'allocated_hours': 0.0,
            'session_rate': 100.0,
        })
        self.assertEqual(project.session_budget, 0.0)

    def test_remaining_session_computation(self):
        project = self.Project.create({
            'name': 'Test Remaining Session Project',
            'allocated_hours': 20.0,
            'session_rate': 50.0,
            'effective_hours': 5.0,
        })
        # session_budget = 1000, remaining = 1000 - (5 * 50) = 750
        self.assertAlmostEqual(project.remaining_session, 750.0, places=2)

    def test_remaining_session_zero_with_missing_data(self):
        project = self.Project.create({
            'name': 'Zero Remaining Project',
            'session_rate': 0.0,
            'effective_hours': 5.0,
        })
        self.assertEqual(project.remaining_session, 0.0)

    def test_closed_field_default_and_usage(self):
        project = self.Project.create({
            'name': 'Closed Field Project',
            'allocated_hours': 10,
            'session_rate': 100,
        })
        self.assertFalse(project.closed)
        project.closed = True
        self.assertTrue(project.closed)

    def test_default_stages_applied_on_create(self):
        project = self.Project.create({
            'name': 'Stage Linked Project',
            'allocated_hours': 10,
            'session_rate': 100,
        })
        self.assertIn(self.default_stage, project.type_ids)
'''
from odoo.tests.common import TransactionCase
class TestProjectProject(TransactionCase):
    def setUp(self):
        super(TestProjectProject, self).setUp()
        self.Project = self.env['project.project']
        self.TaskType = self.env['project.task.type']
    def test_create_project_with_default_stages(self):
        # Positive test case: Create a project and check if default stages are assigned
        task_type = self.TaskType.create({'name': 'Default Stage', 'project_default_stage': True})
        project = self.Project.create({
            'name': 'Test Project',
            'allocated_hours': 10,
            'session_rate': 100.0,
        })
        self.assertTrue(project.type_ids, "Default task stages should be assigned to the project.")
    def test_create_project_without_default_stages(self):
        # Negative test case: Create a project without default stages
        project = self.Project.create({
            'name': 'Test Project Without Stages',
            'allocated_hours': 10,
            'session_rate': 100.0,
        })
        self.assertFalse(project.type_ids, "No default task stages should be assigned to the project.")
    def test_compute_session_budget(self):
        # Positive test case: Compute session budget correctly
        project = self.Project.create({
            'name': 'Test Project Budget',
            'allocated_hours': 10,
            'session_rate': 50.0,
        })
        self.assertEqual(project.session_budget, 500.0, "Session budget should be 500.0")
    def test_compute_session_budget_with_zero_rate(self):
        # Negative test case: Session budget should be zero if session rate is zero
        project = self.Project.create({
            'name': 'Test Project Zero Rate',
            'allocated_hours': 10,
            'session_rate': 0.0,
        })
        self.assertEqual(project.session_budget, 0.0, "Session budget should be 0.0")
    def test_compute_remaining_session(self):
        # Positive test case: Compute remaining session correctly
        project = self.Project.create({
            'name': 'Test Project Remaining Session',
            'allocated_hours': 10,
            'session_rate': 50.0,
            'effective_hours': 5,
        })
        self.assertEqual(project.remaining_session, 250.0, "Remaining session should be 250.0")
    def test_compute_remaining_session_with_no_effective_hours(self):
        # Negative test case: Remaining session should be equal to session budget if no effective hours
        project = self.Project.create({
            'name': 'Test Project No Effective Hours',
            'allocated_hours': 10,
            'session_rate': 50.0,
            'effective_hours': 0,
        })
        self.assertEqual(project.remaining_session, 500.0, "Remaining session should be equal to session budget")
    def test_compute_remaining_session_with_exceeding_effective_hours(self):
        # Edge case: Effective hours exceeding allocated hours
        project = self.Project.create({
            'name': 'Test Project Exceeding Hours',
            'allocated_hours': 10,
            'session_rate': 50.0,
            'effective_hours': 15,
        })
        self.assertEqual(project.remaining_session, -250.0, "Remaining session should be negative if effective hours exceed allocated hours")
    def test_create_project_with_closed_flag(self):
        # Test project creation with closed flag
        project = self.Project.create({
            'name': 'Closed Project',
            'closed': True,
            'allocated_hours': 10,
            'session_rate': 100.0,
        })
        self.assertTrue(project.closed, "The project should be marked as closed.")