# -*- coding: utf-8 -*-
{
    'name': 'Sales Order Followup',

    'summary': """ Sales Order Followup """,

    'description': """
        Sales Order Followup
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Sales',
    'version': '1.0',

    'depends': [
        'sales_team',
        'sale_management',
        'school_finance',
        'sale_aging',
    ],

    'data': [
        'views/res_partner_views.xml',
    ],
}