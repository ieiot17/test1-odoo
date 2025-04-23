{
    'name': 'Project Session Management',
    'version': '1.0',
    'summary': 'Adds session budget and remaining sessions to projects',
    'description': """
        This module extends the Project app to include computed fields:
        - Session Rate
        - Session Budget
        - Remaining Session
    """,
    'category': 'Project',
    'author': 'Your Name or Company',
    'website': 'https://yourcompany.example.com',
    'depends': ['project','hr_timesheet'],
    'data': [
        # Add your views or security files here if any
        'views/project_project_form.xml',
        # 'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
