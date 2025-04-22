# -*- coding: utf-8 -*-
{
    'name': "Project Timesheet Enhancements",
    'version': '1.0',
    'summary': "Validates timesheet entries and notifies when limits are exceeded.",
    'description': """
        - Prevents logging timesheets for closed projects.
        - Validates timesheet time entries (start < end).
        - Prevents overlapping timesheet entries for the same employee.
        - Restricts logging more than 2 hours on a project unless ERP manager.
        - Notifies project manager if allocated hours are exceeded.
    """,
    'author': "Your Company Name",
    'website': "https://yourcompany.com",
    'category': 'Services/Project',
    'depends': ['base', 'project', 'hr_timesheet', 'hr', 'progen_project_task_type'],
    'data': [
        # Add your views or security files here if any
        'views/account_analytic_line_form.xml',
        'views/account_analytic_line_list.xml',
        # 'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
