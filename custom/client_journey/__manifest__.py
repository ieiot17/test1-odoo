{
    'name': 'Progen CJM Workflow',
    'version': '1.0.0',
    'summary': 'Workflow for Research Plans - Researchers, RMs, Reviewers, and CRM',
    'description': """
        This module manages the CJM workflow including state transitions,
        scorecard evaluations, role-based approvals, and automated activity scheduling.
    """,
    'category': 'Custom',
    'author': 'Your Name or Company',
    'website': 'https://yourwebsite.com',
    'depends': [
        'base',
        'mail',
        'hr',
        'contacts',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/progen_cjm_security.xml',
        'views/progen_cjm_form.xml',
        'views/progen_cjm_menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
