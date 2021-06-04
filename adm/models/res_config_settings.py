# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import safe_eval


class AdmFieldsSettings(models.Model):
    _name = 'adm.fields.settings'
    _description = "Fields settings"

    field_id = fields.Many2one('ir.model.fields', "Field")
    relational_model = fields.Char(related='field_id.relation', store=True)

    name = fields.Char(related='field_id.name')

    parent_id = fields.Many2one('adm.fields.settings', string="Parent")
    parent_relational_model = fields.Char(related='parent_id.relational_model')

    child_ids = fields.One2many('adm.fields.settings', 'parent_id', string="Childs")
    long_name = fields.Char(compute="_compute_long_name", store=True)

    domain = fields.Char('Domain filter')

    def _generate_long_name(self):
        return self.name if not self.parent_id else '%s.%s' % (self.parent_id._generate_long_name(), self.name)

    @api.depends('name', 'field_id', 'parent_id')
    def _compute_long_name(self):
        for field in self:
            field.long_name = field._generate_long_name()

    def apply_domain_in_records(self, records):
        self.ensure_one()
        domain = safe_eval(self.domain or '[]')
        return records.filtered_domain(domain)

    def get_as_list_of_names(self):
        name_list = []

        for field in self:
            name_list.append(field.long_name)
            if field.child_ids:
                name_list.extend(field.child_ids.get_as_list_of_names())
        return name_list


class ResConfigSettings(models.TransientModel):
    """  Settings for school base module """
    _inherit = "res.config.settings"

    adm_current_school_year = fields.Many2one('school_base.school_year',
                                              config_parameter='adm.adm_current_school_year',
                                              string="Current school year")

    adm_application_required_field_ids = fields.Many2many(
        'adm.fields.settings',
        string="Application required fields")

    adm_application_optional_field_ids = fields.Many2many(
        'adm.fields.settings',
        relation='adm_app_optional_field_settings',
        string="Application optional fields")

    adm_mail_inviting_partner_to_application_id = fields.Many2one('mail.template',
                                                                  related='company_id.mail_inviting_partner_to_application_id',
                                                                  readonly=False)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        config_parameter = self.env['ir.config_parameter'].sudo()
        application_required_fields_str = config_parameter.get_param(
            'adm_application_required_field_ids', '')
        application_required_fields = [
            int(e) for e in application_required_fields_str.split(',')
            if e.isdigit()
            ]

        application_optional_fields_str = config_parameter.get_param(
            'adm_application_optional_field_ids', '')
        application_optional_fields = [
            int(e) for e in application_optional_fields_str.split(',')
            if e.isdigit()
            ]

        res.update({
            'adm_application_required_field_ids': application_required_fields,
            'adm_application_optional_field_ids': application_optional_fields,
            })

        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        for settings in self:
            config_parameter = self.env['ir.config_parameter'].sudo()
            config_parameter.set_param(
                'adm_application_required_field_ids', ",".join(
                    map(str, settings.adm_application_required_field_ids.ids)))
            config_parameter.set_param(
                'adm_application_optional_field_ids', ",".join(
                    map(str, settings.adm_application_optional_field_ids.ids)))
