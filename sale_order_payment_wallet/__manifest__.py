# -*- coding: utf-8 -*-
{
    'name': "Sales Order Payment Wallet",

    'summary': """ Sales Order Payment Wallet """,

    'description': """
        Sales Order Payment Pay with Wallet
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
        'wallet',
        'sale_order_payment',
        'sale'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizards/sale_order_pay_with_wallet_wizard_views.xml',
        'views/sale_order_views.xml',
        'views/sale_order_payment_views.xml'
        # 'views/sale_order_payment_views.xml',
    ],
}
