# -*- coding: utf-8 -*-
{
    'name': 'Sales Aging',

    'summary': """ Sales Aging """,

    'description': """
        Sales Aging
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Sales',
    'version': '1.0',

    'depends': [
        'sale_management',
        'school_finance',
    ],

    'data': [
        'views/sale_order_views.xml',
    ],
}