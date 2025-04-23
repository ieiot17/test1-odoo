# __manifest__.py
{
    'name': 'HR Employee Extension',
    'version': '1.0',
    'summary': 'Extends HR Employee model with additional fields',
    'description': 'Adds custom fields to hr.employee such as cost center code, employee type, exempt status, and more.',
    'category': 'Human Resources',
    'author': 'Your Company Name',
    'depends': ['hr', 'hr_holidays', 'hr_hourly_cost', 'hr_org_chart', 'hr_skills', 'hr_timesheet', 'project_timesheet_holidays'],
    'data': [
        # Add your views or security files here if any
        'views/hr_employee_views.xml',
        # 'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
