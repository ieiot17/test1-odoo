from odoo.tests import common
from odoo.exceptions import ValidationError
from datetime import datetime

class TestProjectTaskBudget(common.TransactionCase):

    def setUp(self):
        super().setUp()
        self.Project = self.env['project.project']
        self.Task = self.env['project.task']

        self.project = self.Project.create({
            'name': 'Test Project',
            'allocated_hours': 100.0,
            'session_budget': 10000.0,
        })

    def test_task_budget_computation(self):
        task = self.Task.create({
            'name': 'Test Task',
            'project_id': self.project.id,
            'allocated_hours': 10.0,
        })
        self.assertAlmostEqual(task.task_budget, 1000.0, places=2)

    def test_task_budget_zero_if_missing_project_data(self):
        self.project.allocated_hours = 0  # Avoid divide by zero
        task = self.Task.create({
            'name': 'Budgetless Task',
            'project_id': self.project.id,
            'allocated_hours': 10.0,
        })
        self.assertEqual(task.task_budget, 0)

    def test_task_remaining_budget_computation(self):
        task = self.Task.create({
            'name': 'Remaining Budget Task',
            'project_id': self.project.id,
            'allocated_hours': 10.0,
            'effective_hours': 5.0,
        })
        # task_budget = 1000, cost per hour = 100, consumed = 5*100 = 500
        self.assertAlmostEqual(task.task_remaining_budget, 500.0, places=2)

    def test_task_remaining_budget_zero_allocated(self):
        task = self.Task.create({
            'name': 'Zero Alloc Task',
            'project_id': self.project.id,
            'allocated_hours': 0.0,
            'effective_hours': 5.0,
        })
        self.assertEqual(task.task_remaining_budget, 0)

    def test_task_timesheet_complete(self):
        task = self.Task.create({
            'name': 'Completed Task',
            'project_id': self.project.id,
            'allocated_hours': 8.0,
            'remaining_hours': 0.0,
        })
        self.assertTrue(task.task_timesheet)

    def test_task_timesheet_incomplete(self):
        task = self.Task.create({
            'name': 'Ongoing Task',
            'project_id': self.project.id,
            'allocated_hours': 8.0,
            'remaining_hours': 2.0,
        })
        self.assertFalse(task.task_timesheet)

    def test_negative_allocated_hours_raises_validation_error(self):
        with self.assertRaises(ValidationError):
            self.Task.create({
                'name': 'Invalid Task',
                'project_id': self.project.id,
                'allocated_hours': -5.0,
            })

    def test_onchange_allocated_hours_warning(self):
        task = self.Task.new({
            'name': 'Onchange Task',
            'project_id': self.project.id,
            'allocated_hours': 0,
        })
        result = task._onchange_allocated_hours()
        self.assertIn('warning', result)
        self.assertEqual(result['warning']['title'], "Warning")
