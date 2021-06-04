# -*- coding:utf-8 -*-

from odoo import models, fields, api


class SincroDataParameter(models.Model):
    _name = "sincro_data_base.parameter"

    name = fields.Char(string="Name", required=True)
    type = fields.Selection([
        ('constant', "CONSTANT"),
        ('dinamyc', 'Variable')],string="Type", required=True)
    constant_value = fields.Char(string="Name")
    request_id = fields.Many2one('sincro_data_base.server', string='Request')
    field_value = fields.Many2one('ir.model.fields', string='Field' )

