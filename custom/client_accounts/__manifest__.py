# __manifest__.py
{
    'name': 'Client Account',
    'version': '1.0',
    'category': 'Custom',
    'summary': 'Extended customer profile with billing, contact, and admin details',
    'author': 'Your Company Name',
    'depends': ['base', 'contacts','account'],  # Add others if you extend existing modules
    'data': [
        #'security/ir.model.access.csv',
        'views/client_account_inherit_contacts_form.xml',
        'views/client_account_inherit_contacts_form_1.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
