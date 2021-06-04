# -*- coding: utf-8 -*-
{
    'name': 'Import School Data via Excel File',
    'summary': 'This apps helps to import student data from Excel file',
    'description': '''Allow import an excel file for school base ''',
    'author': 'EduWebGroup',
    'category': 'Admissions',
    'version': '1.0.2',
    'depends': ['base', 'account', 'school_base'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/view_import_data.xml',
    ],
    'installable': True,
    'application': True,
    'qweb': [
    ],
    "images": []
}
