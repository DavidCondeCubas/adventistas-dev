# -*- coding: utf-8 -*-
{
    'name': "Adm Custon",

    'summary': """Custom module for adventistas admission""",

    'description': """
           
    """,

    'author': "Eduweb Group",
    'website': "http://www.eduwebgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Admission',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['adm'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
#         'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
