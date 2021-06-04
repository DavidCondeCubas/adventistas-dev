# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class View(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection(selection_add=[('adm_tracking_fields', 'Adm Tracking Fields')])