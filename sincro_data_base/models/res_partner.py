#-*- coding:utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = "res.partner"

    sincro_data_id = fields.Char(string="Full Fabric Profile ID")