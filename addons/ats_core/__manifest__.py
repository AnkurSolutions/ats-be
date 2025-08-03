# addons/ats_core/__manifest__.py

{
    'name': 'ATS Core',
    'version': '1.0',
    'summary': 'Core models shared across ATS modules (skills, locations, etc.)',
    'author': 'Your Company',
    'category': 'Human Resources',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'data/ats_state_data.csv',
        'data/ats_lga_lagos_data.csv',
        'data/ats_skill_data.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
