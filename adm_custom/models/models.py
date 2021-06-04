# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class adm_custom(models.Model):
#     _name = 'adm_custom.adm_custom'
#     _description = 'adm_custom.adm_custom'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
