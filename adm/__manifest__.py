# -*- coding: utf-8 -*-

{
    'name': "Admission School",

    'summary': """""",

    'description': """""",

    'author': "Eduweb Group SL",

    'website': "http://www.eduwebgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data
    # /ir_module_category_data.xml
    # for the full list
    'category': 'Admission',
    'version': '0.11.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'school_base',
        'mail',
        'website',
        'contacts',
        'school_finance',
        'tuition_plan',
        ],

    # always loaded
    'data': [
        # Security
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'data/menudata.xml',

        # Backend views
        'views/adm_application_status_views.xml',
        'views/adm_application_views.xml',
        'views/product_category_views.xml',
        'views/adm_application_page.xml',
        'views/adm_application_questions_views.xml',
        'views/adm_contact_time_views.xml',
        'views/adm_degree_program_views.xml',
        'views/adm_inquiry_views.xml',
        'views/adm_language_level_views.xml',
        'views/adm_language_views.xml',
        'views/assets.xml',
        'views/res_config_settings_views.xml',
        # 'views/res_partner_views.xml',
        'views/res_user_views.xml',
        'views/school_base_models_views.xml',

        # Web templates
        'views/web/portal_templates.xml',
        'views/web/application/menu/family/template_application_family_info.xml',
        'views/web/application/menu/family/template_application_family_finance.xml',
        'views/web/application/menu/family/template_application_family_relationships.xml',
        'views/web/application/menu/template_application_additional_questions.xml',
        'views/web/application/menu/template_application_health.xml',
        'views/web/application/menu/template_application_menu.xml',
        'views/web/application/menu/template_application_tuition_plan.xml',
        'views/web/application/menu/template_application_menu_instructions.xml',
        'views/web/application/menu/template_application_documents_upload.xml',
        'views/web/application/menu/template_application_page_commons.xml',
        'views/web/application/menu/template_application_parent_questionnaire.xml',
        'views/web/application/menu/template_application_signature.xml',
        'views/web/application/menu/template_application_schools_information.xml',
        'views/web/application/menu/template_application_student_info.xml',

        'views/web/application/template_application_create_application.xml',
        'views/web/application/template_application_list.xml',
        'views/web/application/template_application_invite_partner.xml',
        'views/web/application/template_application_menu_progress.xml',

        'views/web/inquiry/template_inquiry_form.xml',

        'data/sequences_data.xml',
        'data/statics_data.xml',
        'data/email_template_data.xml',
        'data/language_types.xml',
        'data/status_type_data.xml',
        'data/gender_data.xml',
        'data/default_page_structure.xml',

        # Wizard
        'wizard/sale_confirm_limit_wizard.xml',
        'wizard/download_application_attachments.xml',

        # Reports
        'report/adm_application_reports.xml',
        'report/adm_activity_report_views.xml',
        'report/grade_level_student_count_views.xml',
        ],
    'qweb': [
        'static/src/xml/kanban_view_button.xml',
        'static/src/xml/attachment_widget.xml',
        ],
    'application': True
}
