# addons/ats_applicant/__manifest__.py

{
    'name': 'ATS Applicant Portal',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Applicant profiles, skills, and job applications for ATS',
    'description': """
        This module allows applicants to create profiles, upload resumes, and apply to jobs.
        Applications are linked to jobs and can be tracked in real time.
    """,
    'author': 'Your Company',
    'website': 'https://yourcompany.com',
    'depends': ['base', 'ats_job'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}