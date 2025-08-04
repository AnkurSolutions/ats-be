{
    "name": "ATS Job",
    "version": "1.0",
    "summary": "Custom ATS job posting and approval workflow",
    "author": "Your Company",
    'depends': ['base', 'hr', 'ats_core'],
    'data': [
        'security/ir.model.access.csv',
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
    'license': 'LGPL-3',
}