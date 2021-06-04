# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
import json


class ConfiguratorPanel(models.Model):
    _name = 'sincro_data_base.configuration_panel'

    sequence = fields.Integer(readonly=True, default=-1)
    name = fields.Char(string="Name")
    # parent_id = fields.Many2one('import_to_facts.configuration_panel', string='Parent field')
    # parent_id = fields.Many2one("res.partner", string="Customer")
    field_id = fields.Many2one('ir.model.fields', string='Odoo field', store=True)

    # reportarlo como bug de odoo
    # model_field_id = fields.Many2one(string="Model Field", related="field_id.model_id", readonly=True)
    # model_field = fields.Char(string="Model Field", related="field_id.model", readonly=True)

    model_name = fields.Char(string="Model Name")
    alias_field = fields.Char('Alias')
    domain = fields.Char("Domain")
    parent_model = fields.Many2one('ir.model', string='Parent Model')
    parent_id = fields.Many2one("sincro_data_base.configuration_panel", string="Parent ID")
    fields = fields.One2many("sincro_data_base.configuration_panel", "parent_id",
                             string="Configuration Panel Childs")

    @api.model
    def create(self, values):
        next_order = self.env['ir.sequence'].next_by_code('sequence.application.task')
        values['sequence'] = next_order
        return super().create(values)

    @api.onchange("field_id")
    def _get_model_name(self):
        if self.field_id.model:
            self.model_name = str(self.field_id.model)

    def get_value(self, key, value):
        if isinstance(value, dict) and str(key) in value:
            return self.get_value(key, value[key])
        else:
            return value

    # devuelve formato pretty del JSON
    def json_to_pretty_format(self, val, json_pretty):
        if not isinstance(val, list) and not isinstance(val, dict) and isinstance(val, str):
            return val
        for key, item in val.items():
            json_pretty[key] = {}
            if isinstance(item, dict) and str(key) in item:
                # json_pretty[key] = self.json_to_pretty_format(item[key], json_pretty[key])
                json_pretty[key] = self.get_value(key, item[key])
            elif isinstance(item, list):
                json_pretty[key] = []
                for elem in item:
                    json_pretty[key].append({})
                    json_pretty[key].append(self.json_to_pretty_format(elem, json_pretty[key].pop()))
            else:
                json_pretty[key] = self.json_to_pretty_format(item, json_pretty[key])
        return json_pretty

    def recur_pretty(self, data, res_json):
        if not isinstance(data, dict):
            return data
        else:
            for key, value in data.items():
                if isinstance(value, dict) and str(key) in value:
                    res_json[key] = self.recur_pretty(value, res_json[key])
                else:
                    res_json[key] = value
                self.recur_pretty(value, res_json[key])

        # devuelve la información en formato json dependiendo de la configuracion del webservice

    def get_json_from_config(self, value, data):
        result = ''
        if not value.fields:
            result += '"%s": "%s",' % (value.alias_field, data)
        else:
            result += '"%s":{' % value.alias_field
            if value.field_id.ttype in ('one2many', 'many2many'):
                result = result[0: -1] + '[{'
            for item_data in data:
                # if len(data) > 1:
                for item in value.fields:
                    aux_val = item_data[item.field_id.sudo().name]
                    # capamos los ids filtrados anteriormente
                    aux_domain = safe_eval(item.domain or "[]")
                    if len(aux_domain) > 0:
                        aux_domain.append(['id', 'in', aux_val.ids])
                        # aux_domain
                        aux_val = item_data[item.field_id.sudo().name].search(aux_domain)

                    result += self.get_json_from_config(item, aux_val)

                if len(data) > 1:
                    # if value.field_id.ttype in ('one2many', 'many2many'):
                    if result[-1] == ',':
                        result = result[0: -1]
                    result += '},{'
                # if len(data) > 1:
            if str(result[-2]) + str(result[-1]) == ',{':
                result = result[0: -3]
            if result[-1] == ',':
                result = result[0: -1]
            if value.field_id.ttype in ('one2many', 'many2many'):
                result += '}]'
            else:
                result += '}'

            result += ','
        return result

    def cleaned_json(self, value, appl):
        raw_res = self.get_json_from_config(value, appl)
        if raw_res[-1] == ',':
            raw_res = raw_res[0: -1]
        if raw_res[-2::] == '}]':
            raw_res += '}'
        json_res = '{' + raw_res + '}';
        return json_res

    def get_json(self, selected_config, item, pretty):

        """ Definiendo la url desde donde va ser posible acceder, tipo de
        metodo,
        cors para habiltiar accesos a ip externas.
        """

        json_res = self.cleaned_json(selected_config, item);
        json_aux = json.loads(json_res)
        json_res = json.dumps(json_aux[list(json_aux.keys())[0]])
        #     idx += 1
        #
        # json_aux_res += ']}'

        # tomamos parametro que nos indica si queremos un formato comprimido (si solo tiene un elemento
        # dentro de un value del dictionario entonces toma ese valor y lo sube de nivel)
        # Example:
        # {"applid": {"FACTSid": {"FACTSid_inner": "False"}}} equivale a {"applid": {"FACTSid": "False"}}

        if pretty:
            json_pretty = {}
            json_res = json.dumps(self.json_to_pretty_format(json.loads(json_res), json_pretty))

        return json_res
