# -*- coding:utf-8 -*-

from odoo import models, fields, api


class IrActionsActWindow(models.Model):
    _inherit = "ir.actions.act_window"

    sync_id = fields.Char(string="Sync ID", readonly=True)
