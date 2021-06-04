# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ActWindowView(models.Model):
    _inherit = 'ir.actions.act_window.view'

    view_mode = fields.Selection(selection_add=[('adm_tracking_fields', 'Adm Tracking Fields')])
