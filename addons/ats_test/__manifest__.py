{
    'name': 'ATS Test',
    'version': '1.0.0',
    'summary': 'Applicant Test Management',
    'depends': ['hr_recruitment'],
    'data': [
        'security/ir.model.access.csv',
        'views/ats_test_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
