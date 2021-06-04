# -*- coding:utf-8 -*-

from odoo import models, fields, api


class SincroDataAPI(models.Model):
    _name = "sincro_data_base.api"
    _description = "Sincro Data Request"

    method = fields.Char(string="Method")
    name = fields.Char(string="Name",
                       required=True)
    base_url = fields.Char(string="Base URL",
                           required=True)
    # api_key = fields.Char(string="API Key",
    #                       required=True)
    # ud_fields = fields.Many2many("sincro_data_base.group_type_ud",
    #                              string="User Defineds",
    #                              store=True,
    #                              relation='sincro_data_api_ud_rel')
    request_ids = fields.One2many("sincro_data_base.server", "api_id")
    header_ids = fields.One2many("sincro_data_base.header", "api_id", string="Headers")