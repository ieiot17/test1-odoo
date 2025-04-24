{
    'name': 'Project Task Type Extension',
    'version': '1.0',
    'summary': 'Sets default task stages',
    'description': """
        This module extends project management by adding computed fields:
        - Project: Session Rate, Session Budget, Remaining Sessions
        - Task: Task Budget, Task Remaining Budget, Task Timesheet
    """,
    'category': 'Project',
    'author': 'Your Company Name',
    'depends': ['project','hr_timesheet','progen_project_extension'],
    'data': [
        # XML files (views) go here if needed
        'views/project_task_type_form.xml',
        # 'views/project_task_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
