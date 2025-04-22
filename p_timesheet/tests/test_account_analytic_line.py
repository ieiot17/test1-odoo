import unittest
from unittest.mock import MagicMock
from datetime import date, timedelta

from odoo.tests import common
from odoo.exceptions import UserError, ValidationError


class TestAnalyticLine(common.TransactionCase):

    def setUp(self):
        super().setUp()
        self.today = date.today()
        self.AnalyticLine = self.env['account.analytic.line']
        self.Project = self.env['project.project']
        self.Employee = self.env['hr.employee']
        self.User = self.env['res.users']

        self.GroupERPManager = self.env.ref('base.group_erp_manager')
        self.GroupYesterdayToday = self.env.ref('progen.progen_crm')
        self.GroupLastMonthToday = self.env.ref('base.group_erp_manager')

        # Setup test data
        self._create_employees_and_users()
        self._create_projects()

    def _create_employees_and_users(self):
        self.employee1 = self.Employee.create({'name': 'Test Employee 1'})
        self.employee2 = self.Employee.create({'name': 'Test Employee 2'})

        self.user_employee1 = self._create_user('emp1', [self.employee1.id])
        self.user_manager = self._create_user('manager', [], [self.GroupERPManager.id])
        self.user_yesterday_today = self._create_user('yesterday', [], [self.GroupYesterdayToday.id])
        self.user_last_month_today = self._create_user('lastmonth', [], [self.GroupLastMonthToday.id])

    def _create_user(self, login, employee_ids=None, groups=None):
        user = self.User.create({'name': f'User {login}', 'login': login})
        if employee_ids:
            user.write({'employee_ids': [(6, 0, employee_ids)]})
        if groups:
            user.write({'groups_id': [(4, gid) for gid in groups]})
        return user

    def _create_projects(self):
        self.project1 = self.Project.create({'name': 'Test Project 1', 'allocated_hours': 10})
        self.project_closed = self.Project.create({'name': 'Closed Project', 'closed': True})

    def _get_env_for_user(self, user):
        return self.env(user=user)['account.analytic.line']

    # ----------------------------
    # Core Functional Tests
    # ----------------------------

    def test_create_timesheet_on_closed_project(self):
        """Creating a timesheet on a closed project should raise UserError."""
        with self.assertRaises(UserError):
            self.AnalyticLine.create({
                'project_id': self.project_closed.id,
                'employee_id': self.employee1.id,
                'date': self.today,
                'unit_amount': 1.0,
            })

    def test_write_timesheet_on_closed_project(self):
        """Writing to a closed project should not be allowed."""
        timesheet = self.AnalyticLine.create({
            'project_id': self.project1.id,
            'employee_id': self.employee1.id,
            'date': self.today,
            'unit_amount': 1.0,
        })
        with self.assertRaises(UserError):
            timesheet.write({'project_id': self.project_closed.id})

    def test_create_timesheet_triggers_notification(self):
        """Creating timesheet exceeding limit should trigger notification."""
        mock_notifier = MagicMock()
        with unittest.mock.patch('odoo.addons.your_module_name.models.analytic_line.ProjectNotifier', return_value=mock_notifier):
            self.AnalyticLine.create({
                'project_id': self.project1.id,
                'employee_id': self.employee1.id,
                'date': self.today,
                'unit_amount': 11.0,
            })
            mock_notifier.notify_if_exceeded.assert_called_once()

    def test_write_timesheet_triggers_notification(self):
        """Updating timesheet to exceed limit should notify."""
        timesheet = self.AnalyticLine.create({
            'project_id': self.project1.id,
            'employee_id': self.employee1.id,
            'date': self.today,
            'unit_amount': 1.0,
        })
        mock_notifier = MagicMock()
        with unittest.mock.patch('odoo.addons.hr_time.models.analytic_line.ProjectNotifier', return_value=mock_notifier):
            timesheet.write({'unit_amount': 11.0})
            mock_notifier.notify_if_exceeded.assert_called_once()

    # ----------------------------
    # Time Validation Logic
    # ----------------------------

    def test_check_time_policies_valid_time(self):
        """Valid start and end times should calculate unit_amount."""
        timesheet = self.AnalyticLine.create({
            'project_id': self.project1.id,
            'employee_id': self.employee1.id,
            'date': self.today,
            'start_time': '0900',
            'end_time': '1000',
        })
        self.assertEqual(timesheet.unit_amount, 1.0)

    def test_check_time_policies_start_time_after_end_time(self):
        """Start time after end time should raise ValidationError."""
        with self.assertRaises(ValidationError):
            self.AnalyticLine.create({
                'project_id': self.project1.id,
                'employee_id': self.employee1.id,
                'date': self.today,
                'start_time': '1000',
                'end_time': '0900',
            })

    def test_check_time_policies_overlapping_timesheet(self):
        """Overlapping timesheet entries should not be allowed."""
        self.AnalyticLine.create({
            'project_id': self.project1.id,
            'employee_id': self.employee1.id,
            'date': self.today,
            'start_time': '0900',
            'end_time': '1100',
        })
        with self.assertRaises(ValidationError):
            self.AnalyticLine.create({
                'project_id': self.project1.id,
                'employee_id': self.employee1.id,
                'date': self.today,
                'start_time': '1000',
                'end_time': '1200',
            })

    def test_overlap_skips_lines_with_missing_times(self):
        """Lines with missing times should be skipped when checking for overlaps."""
        env = self._get_env_for_user(self.user_employee1)
        env.create({
            'project_id': self.project1.id,
            'employee_id': self.employee1.id,
            'date': self.today,
            'start_time': None,
            'end_time': None,
            'unit_amount': 1.0,
        })
        env.create({
            'project_id': self.project1.id,
            'employee_id': self.employee1.id,
            'date': self.today,
            'start_time': '0900',
            'end_time': '1000',
        })

    # ----------------------------
    # Hour Limit & Role Permissions
    # ----------------------------

    def test_check_total_hours_exceed_limit_no_manager(self):
        env = self._get_env_for_user(self.user_employee1)
        env.create({
            'project_id': self.project1.id,
            'employee_id': self.employee1.id,
            'date': self.today,
            'start_time': '0800',
            'end_time': '0900',
        })
        with self.assertRaises(ValidationError):
            env.create({
                'project_id': self.project1.id,
                'employee_id': self.employee1.id,
                'date': self.today,
                'start_time': '0900',
                'end_time': '1130',
            })

    def test_check_total_hours_not_exceed_limit_manager(self):
        env = self._get_env_for_user(self.user_manager)
        env.create({'project_id': self.project1.id, 'employee_id': self.employee1.id, 'date': self.today, 'start_time': '0800', 'end_time': '1000'})
        env.create({'project_id': self.project1.id, 'employee_id': self.employee1.id, 'date': self.today, 'start_time': '1000', 'end_time': '1300'})
        self.assertEqual(env.search_count([('employee_id', '=', self.employee1.id)]), 2)

    # ----------------------------
    # Date-Based Group Restrictions
    # ----------------------------

    def test_check_date_permissions_yesterday_today_valid(self):
        env = self._get_env_for_user(self.user_yesterday_today)
        env.create({'project_id': self.project1.id, 'employee_id': self.employee1.id, 'date': self.today, 'unit_amount': 1.0})
        env.create({'project_id': self.project1.id, 'employee_id': self.employee1.id, 'date': self.today - timedelta(days=1), 'unit_amount': 1.0})
        self.assertEqual(env.search_count([('employee_id', '=', self.employee1.id)]), 2)

    def test_check_date_permissions_yesterday_today_invalid(self):
        env = self._get_env_for_user(self.user_yesterday_today)
        with self.assertRaises(UserError):
            env.create({
                'project_id': self.project1.id,
                'employee_id': self.employee1.id,
                'date': self.today - timedelta(days=2),
                'start_time': '0800',
                'end_time': '1000',
                'unit_amount': 1.0,
            })

    def test_check_date_permissions_last_month_today_valid(self):
        env = self._get_env_for_user(self.user_last_month_today)
        dates = [self.today, self.today - timedelta(days=15), self.today - timedelta(days=30)]
        for d in dates:
            env.create({'project_id': self.project1.id, 'employee_id': self.employee1.id, 'date': d, 'unit_amount': 1.0})
        self.assertEqual(env.search_count([('employee_id', '=', self.employee1.id)]), 3)

    def test_check_date_permissions_last_month_today_invalid(self):
        env = self._get_env_for_user(self.user_last_month_today)
        with self.assertRaises(UserError):
            env.create({
                'project_id': self.project1.id,
                'employee_id': self.employee1.id,
                'date': self.today - timedelta(days=31),
                'start_time': '0800',
                'end_time': '1000',
                'unit_amount': 1.0,
            })

    def test_check_date_permissions_no_specific_group(self):
        env = self._get_env_for_user(self.user_employee1)
        with self.assertRaises(UserError):
            env.create({
                'project_id': self.project1.id,
                'employee_id': self.employee1.id,
                'date': self.today,
                'start_time': '0900',
                'end_time': '1130',
                'unit_amount': 1.0,
            })

    def test_check_hhmm_format_valid(self):
        """Invalid HHMM formats or missing times should raise UserError."""
        env = self._get_env_for_user(self.user_employee1)
        with self.assertRaises(UserError):
            env.create({'project_id': self.project1.id, 'employee_id': self.employee1.id, 'date': self.today, 'start_time': '3900', 'end_time': '1130'})
        with self.assertRaises(UserError):
            env.create({'project_id': self.project1.id, 'employee_id': self.employee1.id, 'date': self.today, 'start_time': 'abcd', 'end_time': '1e130'})
        with self.assertRaises(UserError):
            env.create({'project_id': self.project1.id, 'employee_id': self.employee1.id, 'date': self.today, 'start_time': None, 'end_time': None})

