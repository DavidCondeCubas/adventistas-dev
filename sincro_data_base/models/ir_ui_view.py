#-*- coding:utf-8 -*-

from odoo import models, fields, api

class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    sync_id = fields.Char(string="Sync ID", readonly=True)