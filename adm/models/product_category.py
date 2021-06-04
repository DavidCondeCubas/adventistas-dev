# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductCategory(models.Model):
    _inherit = 'product.category'

    active_admission = fields.Boolean()
