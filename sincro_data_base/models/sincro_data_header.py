# -*- coding:utf-8 -*-

from odoo import models, fields, api


class SincroDataHeader(models.Model):
    _name = "sincro_data_base.header"

    name = fields.Char(string="Name")
    value = fields.Char(string="Value")
    api_id = fields.Many2one('sincro_data_base.api', string="Related API")
