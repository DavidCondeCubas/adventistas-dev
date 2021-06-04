# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    """  Settings for school base module """
    _inherit = "res.config.settings"

    api_configurator_ids = fields.Many2many(
        'sincro_data_base.api',
        string="APIS",
        store=True,
        relation='sincro_data_api_configurator_relation')

    # api_configurator_ids = fields.One2many("sincro_data_base.api", "config_id", "APIS")

    webservice_configurator_ids = fields.Many2many(
        'sincro_data_base.webservice_configurator',
        string="Webservice Configurator",
        store=True,
        relation='sincro_data_base_config_webservice_configurator')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        config_parameter = self.env['ir.config_parameter'].sudo()

        # adm_application_webservice_configurator_str = config_parameter.get_param(
        #     'webservice_configurator_ids', '')
        # webservice_configurator_fields = [
        #     int(e) for e in adm_application_webservice_configurator_str.split(',')
        #     if e.isdigit()
        # ]

        api_configurator_str = config_parameter.get_param(
            'api_configurator_ids', '')
        api_configurator_fields = [
            int(e) for e in api_configurator_str.split(',')
            if e.isdigit()
        ]

        webservice_configurator_str = config_parameter.get_param(
            'webservice_configurator_ids', '')
        webservice_configurator_fields = [
            int(e) for e in webservice_configurator_str.split(',')
            if e.isdigit()
        ]

        res.update({
            'webservice_configurator_ids': webservice_configurator_fields,
            'api_configurator_ids': api_configurator_fields
        })

        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        for settings in self:
            config_parameter = self.env['ir.config_parameter'].sudo()
            # config_parameter.set_param(
            #     'webservice_configurator_ids', ",".join(
            #         map(str, settings.webservice_configurator_ids.ids)))

            config_parameter.set_param(
                'api_configurator_ids', ",".join(
                    map(str, settings.api_configurator_ids.ids)))

            config_parameter.set_param(
                'webservice_configurator_ids', ",".join(
                    map(str, settings.webservice_configurator_ids.ids)))
