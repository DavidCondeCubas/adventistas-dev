# -*- coding: utf-8 -*-
{
    'name': "Sales Order Payment",

    'summary': """ Register payment inside Sales Order """,

    'description': """
        Register payment inside Sales Order
    """,

    'author': "Eduwebgroup",
    'website': "http://www.eduwebgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Administration',
    'version': '0.14',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sale',
        'account'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/sale_order_payment_views.xml',
        'views/res_company_views.xml',
        'wizards/sale_order_register_payment_wizard_views.xml',
        'wizards/sale_order_reconcile_payment_wizard_views.xml'
    ],
}
