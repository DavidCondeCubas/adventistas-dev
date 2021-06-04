# -*- coding:utf-8 -*-

from odoo import models, fields, api


class SincroDataMapped(models.Model):
    _name = "sincro_data_base.mapped"
    _description = "Sincro Data Mapped"

    json_key = fields.Char("JSON key")
    field_id = fields.Many2one('ir.model.fields', string='Model field', store=True)
    field_model_id = fields.Char(related='field_id.relation', readonly=True)
    key_field_id = fields.Many2one('ir.model.fields', string='Model field Key', store=True)
    server_id = fields.Many2one("sincro_data_base.server", readonly=True)
    model_id = fields.Many2one("ir.model", string="Model", readonly=True, related="server_id.model_id")
    conditional_value = fields.Char(string="Conditional value")
    concat_value = fields.Char(string="Contact value")
    default_value = fields.Char(string="Default value")
    is_active = fields.Boolean("Sincronize", default=True)
    is_force_create = fields.Boolean("Force created", default=False)
    is_force_overwrite = fields.Boolean("Force Overwrite", default=True)
    is_an_img_from_url = fields.Boolean("URL Img", default=False)
    is_default = fields.Boolean("Field by default", default=True)
    is_field_required = fields.Boolean(related="field_id.required")

    def name_get(self):
        return [(record.id, '%s' % record.json_key) for record in self]

    @api.onchange("is_active")
    def _reset_booleans(self):
        for record in self:
            if not record.is_active:
                record.is_force_create = False
                record.is_force_overwrite = False
                record.is_an_img_from_url = False
