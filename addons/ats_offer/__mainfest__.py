{
    'name': 'ATS Offer',
    'version': '1.0.0',
    'summary': 'Manage job offers for applicants',
    'depends': ['hr_recruitment'],
    'data': [
        'security/ir.model.access.csv',
        'views/ats_offer_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
