# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class WebserviceConfigurator(models.Model):
    _name = 'sincro_data_base.webservice_configurator'

    name = fields.Char("Name")
    panel_configuration = fields.Many2one("sincro_data_base.configuration_panel", string="Configuration Panel")
    domain = fields.Char("Domain")
    pretty = fields.Boolean("Pretty")
    label = fields.Char("Label")
    model_id = fields.Many2one('ir.model', string='Model')
    model_name = fields.Char(string="Model Name", store=True)

    @api.onchange("model_id")
    def _get_model_name(self):
        if self.model_id.model:
            self.model_name = str(self.model_id.model)
