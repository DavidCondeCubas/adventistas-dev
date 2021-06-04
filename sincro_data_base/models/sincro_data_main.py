# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Main(models.Model):
    _name = 'sincro_data_base.main'

    api_list = fields.Many2one("sincro_data_base.server", string="APIs")