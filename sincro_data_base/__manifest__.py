# -*- coding: utf-8 -*-
{
    'name': "Sincro Data Base",

    'summary': """ Tool for the importation from Odoo to API´s """,

    'description': """
        Common models for eduwebgroup school modules
    """,

    'author': "Eduwebgroup",
    'website': "http://www.eduwebgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list

    'category': 'Admission',
    'version': '1.2.1',
    # any module necessary for this one to work correctly, esta acoplado debido a adm debido al wizard
    # se debe desacoplar extrayendo esta funcionalidad en un submodulo
    'depends': ['base', 'base_automation', 'school_base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'views/sincro_data_api_views.xml',
        'views/sincro_data_server_views.xml',
        'views/sincro_data_header_views.xml',
        'views/sincro_data_log_views.xml',
        'views/sincro_data_log_telegram_bot.xml',
        'views/sincro_data_parameter_views.xml',
        'views/sincro_data_panel_configuration_views.xml',
        'views/sincro_data_webservice_configurator_views.xml',
        'views/sincro_data_mapped_views.xml',
        'views/inherited/res.partner.xml',

        'views/config_views.xml',
        'data/ir_cron_data.xml',
        'data/mail_template_data.xml',

        # wizard
        'wizard/wizard.xml',

        # CSS
        'static/src/xml/sincro_data_base_server.xml',
    ],
    'qweb': [
        'static/src/xml/kanban_view_button.xml'],
    'demo': []
}
