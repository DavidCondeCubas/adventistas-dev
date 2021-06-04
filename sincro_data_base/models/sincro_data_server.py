# -*- coding:utf-8 -*-

import base64
import logging
from distutils.command.config import config

import requests
import json
import re

from datetime import datetime, timedelta
from pathlib import Path
from pprint import pprint as pp

# from doc._extensions.html_domain import address
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import MissingError, UserError
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError
from datetime import timedelta

_logger = logging.getLogger(__name__)

REGEX_EMAIL = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
MAX_INT = 2147483647


class FullFabricServer(models.Model):
    _name = "sincro_data_base.server"
    _description = "Sincro Data Server"
    name = fields.Char(string="Name",
                       required=True)
    api_name = fields.Char(string="Request Name", related="api_id.name", readonly=True)
    api_base_url = fields.Char(string="Base URL", related="api_id.base_url", readonly=True)
    api_header_ids = fields.One2many(string="API headers", related="api_id.header_ids", readonly=True)
    model_id = fields.Many2one("ir.model", string="Model", required=True)
    api_id = fields.Many2one("sincro_data_base.api", string="API")
    path = fields.Char(string="Path")
    domain = fields.Char("Domain")
    test_item_model_id = fields.Integer('Item ID')
    parameter_ids = fields.Many2many("sincro_data_base.parameter", "request_id", string="Parameters")
    computed_path = fields.Char(string="Computed path", compute="_compute_path", readonly=True)

    state = fields.Selection(
        [("draft", "Draft"), ("subscribed", "Subscribed")],
        required=True,
        default="draft",
    )

    method = fields.Selection([
        ('get', "GET"),
        ('post', "POST"),
        ('put', "PUT"),
        ('delete', "DELETE"),
        ('patch', "PATCH"),
        ('head', "HEAD"),
        ('connect', "CONNECT"),
        ('options', "OPTIONS"),
        ('trace', "TRACE"),
        ('ws_odoo', "WService -> ODOO"),
        ('odoo_ws', "ODOO -> WService"),
    ],
        string="Method", default='get'
    )
    json_pretty = fields.Boolean("Pretty JSON", default=False)
    json_configuration_id = fields.Many2one('sincro_data_base.configuration_panel', string="JSON Configuration")
    json_example = fields.Char(string='JSON Example', compute="_compute_json", readonly=True)
    response_message = fields.Char(string='Response TEXT', compute="_clean_response", store=True, readonly=True)
    response_code = fields.Integer(string="Response code")
    # json_example = fields.Char(string='JSON Example')
    cron_id = fields.Many2one('ir.cron', string="Cron",
                              ondelete="cascade")

    cron_active = fields.Boolean(string="Active", related='cron_id.active')

    interval_minutes = fields.Integer(string="Interval minutes", default=30)

    retrieve_date = fields.Datetime(string="Last Retrieval Date",
                                    readonly=True)

    log_ids = fields.Many2many(string="Created Families",
                               comodel_name="sincro_data_base.log",
                               relation="sincro_data_base_log_rel", store=True)

    skip = fields.Integer(string="Skip")
    limit = fields.Integer(string="Limit",
                           default=100)

    model_name = fields.Char(string="Model Name", store=True)
    retrieve_date_test = fields.Datetime(string="Last Test Date",
                                         readonly=True)

    mapped_fields = fields.Many2many(string="Mapped fields",
                                     comodel_name="sincro_data_base.mapped",
                                     relation="sincro_data_base_mapped_rel", store=True)

    struct_response = fields.Char("Struct response", store=True)
    ws_json = fields.Char("WS JSON", store=True)
    ws_odoo_field_key = fields.Many2one('ir.model.fields', string='External-ODOO Field Key', store=True)
    ws_odoo_field_keys = fields.Many2many('sincro_data_base.mapped', string='External-ODOO Field Keys', store=True)
    ws_odoo_cascade_keys = fields.Many2many(comodel_name='sincro_data_base.mapped',
                                            relation="sincro_data_base_ws_odoo_cascade_fields_rel",
                                            string='Cascade Field Keys', store=True)
    key_json_data = fields.Char("JSON Key Data")
    ws_method = fields.Selection([
        ('get', "GET"),
        ('post', "POST"),
        ('put', "PUT"),
        ('delete', "DELETE"),
        ('patch', "PATCH"),
        ('head', "HEAD"),
        ('connect', "CONNECT"),
        ('options', "OPTIONS"),
        ('trace', "TRACE")
    ], string="WS Method", default='get')

    act_window_id = fields.Many2one('ir.actions.act_window', string='Action Window')
    view_id = fields.Many2one('ir.ui.view', string='View')

    # fields.Many2many('sincro_data_base.mapped', string="Mapped Fields", compute='_compute_mapped_fields')
    # def _get_format_json(self, data, aux_struct_response, num_spaces):
    #       for key, value in data.items():
    #         aux_struct_response += '\n%s"%s":' % (''.ljust(num_spaces), key)
    #         if isinstance(value, list):
    #             aux_struct_response += '"[{...},{...},{...},...]",'
    #         elif isinstance(value, dict):
    #             inner_json_raw = ''
    #             self._get_format_json(value, inner_json_raw, num_spaces * 2)
    #             aux_struct_response += '{%s\n}' % inner_json_raw
    #         else:
    #             aux_struct_response += '%s,' % value

    def _get_format_json(self, key, value, num_spaces):
        # es una lista
        if isinstance(value, list):
            return '\n%s"%s":%s' % (''.ljust(num_spaces), key, '"[{...},{...},{...},...]",')
        # es un diccionario
        elif isinstance(value, dict):
            inner_value = ''
            for key_inner, data in value.items():
                inner_value += '%s,' % self._get_format_json(key_inner, data, num_spaces + 5)

            dict_lbl = ''
            if key:
                dict_lbl = '%s%s:\n' % (''.ljust(num_spaces), key)

            return '\n%s%s{%s\n%s}' % (dict_lbl, ''.ljust(num_spaces), inner_value, ''.ljust(num_spaces))
        # de ñlo cotnrario devolvemos el value
        else:
            return '\n%s"%s":%s' % (''.ljust(num_spaces), key, str(value))

    def _get_keys_mapped(self, key, value, prefix):
        # es un dict
        if isinstance(value, dict):
            inner_list = []
            for key_inner, data in value.items():
                res = self._get_keys_mapped(key_inner, data, '%s' % key)
                # si es una lista entonces las combinamos
                if isinstance(res, list):
                    inner_list += res
                else:
                    if res:
                        inner_list.append(res)
                # += '%s,' % self._get_format_json(key_inner, data, num_spaces + 5)
            return inner_list
        # de ñlo cotnrario devolvemos el valuel
        else:
            return '%s/%s' % (prefix, key) if prefix else str(key)

    # @api.onchange('computed_path', 'model_id', 'key_json_data')
    @api.onchange('model_id', 'key_json_data')
    def _compute_mapped_fields(self):
        # self.mapped_fields = False
        for record in self:
            # borro las relaciones anteriores para linkearlas nuevamente
            # record.mapped_fields.unlink()
            if record.method == 'ws_odoo' and record.computed_path != 'Problems with the configuration of request.':
                headers = {}
                for header in record.api_header_ids:
                    headers[header.name] = header.value
                res = self._send_request(record.computed_path, 'GET', headers, '{}')
                # data = json.loads(res.text)['results']
                if res.status_code != 200:
                    pass
                # AÑADIR LA ALTERNATIVA DE SELECCIONAR CUAL ES EL CAMPO A OBTENER LA INFO DEL  WEB SERVICE
                data = json.loads(res.text)
                # la data esta en un nivel inferior como el webservice de FACTS
                if record.key_json_data and record.key_json_data in data:
                    data = data[record.key_json_data]

                # borramos todos los mapped que no tengan asociados un server_id
                # self.env['sincro_data_base.mapped'].browse(record.mapped_fields.ids).unlink()

                mapped_ids = []
                if isinstance(data, list):
                    key_json_names = self._get_keys_mapped('', data[0], '')
                    env_mapped = self.env['sincro_data_base.mapped']
                    for key in key_json_names:
                        created_mapped = env_mapped.create({
                            'json_key': str(key),
                            'server_id': self.ids[0],
                            # 'field_id': env_mapped.test_item_model_id
                        })
                        mapped_ids.append(created_mapped.id)
                    # for key, value in data[0].items():
                    #     env_mapped = self.env['sincro_data_base.mapped']
                    #     created_mapped = env_mapped.create({
                    #         'json_key': str(key),
                    #         'server_id': self.ids[0],
                    #         # 'field_id': env_mapped.test_item_model_id
                    #     })
                    #     mapped_ids.append(created_mapped.id)

                if isinstance(data, list):
                    aux_struct_response = 'Correct struct: [{...},{...},{...},...]'
                # es un dictionario por tanto ha de seleccionar de que campo tomar la data
                else:
                    # aux_body_json = ''
                    # self._get_format_json(data, aux_body_json, 0)
                    # aux_struct_response = '{%s\n}' % aux_body_json
                    aux_struct_response = '{'
                    for key, value in data.items():
                        aux_struct_response += '\n     "%s":' % key
                        if isinstance(value, list):
                            aux_struct_response += '"[{...},{...},{...},...]",'
                        else:
                            aux_struct_response += '%s,' % value
                    aux_struct_response += '\n}'

                record.struct_response = aux_struct_response
                if mapped_ids:
                    aux_model_id = record.model_id.id
                    record.mapped_fields.unlink()
                    record.mapped_fields = [(6, 0, mapped_ids)]
                    record.model_id = aux_model_id
                if isinstance(data, list) and len(data) > 0:
                    # aux_body_json = ''
                    # self._get_format_json('', data[0], 5)
                    # aux_struct_response = '{%s\n}' % aux_body_json
                    record.ws_json = self._get_format_json('', data[0], 0)
                    # record.ws_json = json.dumps(data[0]).replace(',', ',\n    ').replace('{', '{\n    ').replace('}',
                    #                                                                                              '\n}')

    def get_json_data(self):
        for server in self:
            aux_domain = safe_eval(server.domain or "[]")
            env_mapped = self.env['sincro_data_base.mapped']
            env_aux = server.env[server.model_id.model]
            filtered_items = env_aux.search(aux_domain)
            json_items = []
            for item in filtered_items:
                json_items.append(json.loads(server.json_configuration_id.get_json(server.json_configuration_id,
                                                                                   env_aux.browse(
                                                                                       [item.id]),
                                                                                   server.json_pretty)))
            self.struct_response = json.dumps(json_items)

    def indent_json(self):
        # ya tiene formato se lo quitamos
        if '\n' in self.struct_response:
            self.struct_response = self.struct_response.replace('\n', '').replace(' ', '')
            return
        # le damos el formato de tipo json
        aux_struct_response = '['
        for item in json.loads(self.struct_response):
            aux_struct_response += '\n     {'
            for key, value in item.items():
                aux_struct_response += '\n          "%s":' % key
                if isinstance(value, list):
                    aux_struct_response += '"[{...},{...},{...},...]",'
                else:
                    aux_struct_response += '"%s",' % value
            aux_struct_response = aux_struct_response[:-1] + '\n     },'
        aux_struct_response = aux_struct_response[:-1] + '\n]'

        self.struct_response = aux_struct_response

    def add_mapped_field(self):
        created_mapped = self.env["sincro_data_base.mapped"].create({
            'json_key': 'static_value',
            'server_id': self.id,
        })
        self.mapped_fields = [(4, created_mapped.id)]

    def add_json_mapped_field(self):
        created_mapped = self.env["sincro_data_base.mapped"].create({
            'json_key': 'Write a key of json data',
            'server_id': self.id,
            'is_default': False,
        })
        self.mapped_fields = [(4, created_mapped.id)]

    @api.onchange("model_id")
    def _get_model_name(self):
        if self.model_id.model:
            self.model_name = str(self.model_id.model)

    @api.depends("path", "model_id", "test_item_model_id", "parameter_ids")
    def _compute_path(self):
        for record in self:
            try:
                env_aux = self.env[record.model_id.model]
                if not record.test_item_model_id or record.test_item_model_id == '' or record.test_item_model_id not in \
                        self.env[record.model_id.model].search([]).ids:
                    if env_aux.search([]).ids:
                        record.test_item_model_id = env_aux.search([])[0].id

                record.computed_path = record.api_base_url + record.path % tuple(
                    tuple(map(lambda value: env_aux.browse([record.test_item_model_id])[
                        value.field_value.name] if value.type != 'constant' else value.constant_value,
                              record.parameter_ids)))
            except Exception as e:
                record.computed_path = 'Problems with the configuration of request.'

    @api.depends("json_configuration_id", "model_id", "test_item_model_id", "json_pretty")
    def _clean_response(self):
        for record in self:
            record.response_message = ''

    @api.model
    def create(self, values):
        # values['sequence'] = next_order
        return super().create(values)

    @api.depends("json_configuration_id", "model_id", "test_item_model_id", "json_pretty")
    def _compute_json(self):
        for record in self:
            try:
                env_aux = self.env[record.model_id.model]
                if record.json_configuration_id and env_aux.browse([record.test_item_model_id]):
                    record.json_example = record.json_configuration_id.get_json(record.json_configuration_id,
                                                                                env_aux.browse(
                                                                                    [record.test_item_model_id]),
                                                                                record.json_pretty)
                else:
                    record.json_example = {}
            except:
                record.json_example = {}

    def action_delete_all_data(self):
        for server in self:
            server.move_ids.unlink()
            server.attachment_ids.unlink()
            server.test_ids.unlink()
            # server.program_pathway_ids.unlink()
            server.application_ids.unlink()
            server.student_ids.unlink()
            server.parent_ids.unlink()
            server.family_ids.unlink()
            server.retrieve_date = False

    # def _create_person_facts(self, server, headers):
    #     self.ensure_one()
    #     unknown_students = self._send_request(server.computed_path, 'get', headers, '{}')
    #     if len(json.loads(unknown_students.text)['results']) > 0:
    #         unk_std = json.loads(unknown_students.text)['results'][0]
    #         unk_std_id = unk_std['personId']
    #         env_aux = self.env[self.model_id.model]
    #         computed_path = self.api_base_url + '/People/' % tuple(
    #             reversed(tuple(map(lambda value: env_aux.browse([record.test_item_model_id])[
    #                 value.field_value.name] if value.type != 'constant' else value.constant_value,
    #                                record.parameter_ids))))
    #
    #         return self._send_request(server.computed_path, 'put', headers, self.json_example)
    #     else:
    #         raise ValidationError("No existe usuarios Unknown en FACTS")
    def _create_person_facts(self, server, headers):
        self.ensure_one()
        unknown_students = self._send_request(server.computed_path, 'get', headers, '{}')
        students = json.loads(unknown_students.text)['results']
        env_log = self.env['sincro_data_base.log']
        log_registers = env_log.search([('url', 'like', 'create_facts')])
        # log_registers = env_log.search([])

        created_students = log_registers.mapped(lambda x: x.item_id);
        new_students = list(filter(lambda x: x['personId'] not in created_students, students))

        # selected_students = students.filtered(
        #     lambda app: any(json.loads(app.text)['results']['personId'] not in log_registers))
        if len(new_students) > 0:
            unk_std_id = new_students[0]['personId']
            computed_path = self.api_base_url + '/People/%s' % unk_std_id
            created_res = self._send_request(computed_path, 'put', headers, self.json_example)
            created_log = env_log.create({
                'url': 'create_facts',
                'item_id': unk_std_id,
                'created_date': datetime.now(),
                'status_code': created_res.status_code,
                'request': str(created_res.request.body),
                'response': created_res.text
            })

            return created_res
        else:
            raise ValidationError("No existe usuarios Unknown en FACTS")

    def action_test_connection(self, *args):
        for server in self:
            error_msgs = {}
            headers = {}
            res = False
            for header in server.api_header_ids:
                headers[header.name] = header.value

                # if self.method == 'create_facts':
                #     res = self._create_person_facts(server, headers)
                # else:
                res = self._send_request(server.computed_path, server.method, headers, server.json_example)

                server.response_code = res.status_code
                server.response_message = res.text

                env_log = server.env['sincro_data_base.log']
                server.retrieve_date_test = datetime.now()

                created_log = env_log.create({
                    'url': server.computed_path,
                    'item_id': server.test_item_model_id,
                    'created_date': datetime.now(),
                    'model': str(server.model_id.model),
                    'server_id': server.id,
                    'status_code': res.status_code,
                    'request': str(server.json_example),
                    'response': res.text
                })
                server.log_ids = [(4, created_log.id)]

    def _generate_new_name(self, value, field, model):
        for x in range(MAX_INT):
            new_name = str(value) + ' (%s)' % x
            if not self.env[model].search([(field, '=', new_name)]):
                return new_name

    def _find_in_list(self, application, list_json, fields_to_check, value, field_return_name):
        if len(list_json) == 0:
            application.write({'status_id': self.env['%s.status' % self.model_id.model].search(
                [('sequence', '=', application.status_id.sequence - 1)]).id})
            self._cr.commit()
            raise ValidationError("Problems with the connected to FACTS")
        for field in fields_to_check:
            if field not in list_json[0]:
                application.write({'status_id': self.env['%s.status' % self.model_id.model].search(
                    [('sequence', '=', application.status_id.sequence - 1)]).id})
                self._cr.commit()
                raise ValidationError("A field to checked not exists in the list_json[0]")
        for item in list_json:
            i = 0
            for checked_field in fields_to_check:
                if checked_field in item and str(item[checked_field]) == str(value[checked_field]):
                    i += 1

            if i == len(fields_to_check):
                return item[field_return_name]

        return -1

    # FUNCION QUE COMPRUEBA SI ES False devuelve vacio, el booleano recur determina si es un objeto y comprueba de izquierda a derecha si es vacio para devolver el vacio
    def _clean_false_to_empty(self, value, chain, default_value):
        if not value:
            return default_value
        recur_val = value
        for inner_itm in chain:
            if inner_itm not in recur_val or (inner_itm in recur_val and not recur_val[inner_itm]):
                return default_value
            recur_val = recur_val[inner_itm]

        return recur_val

    def _check_and_create_in_facts(self, check_path, insert_path, headers, json_data):
        res = self._send_request(check_path, 'get', headers, '{}')

        # Si la direccion existe la tomamos del request anterior, de lo contrario la creamos en FACTS
        if 'results' not in json.loads(res.text) or len(json.loads(res.text)['results']) == 0:
            res = self._send_request(insert_path, 'post', headers, json.dumps(json_data))

        return res

    def subscribe(self):
        cron_env = self.env['ir.cron']
        env_id = self.env['ir.model'].search([('model', '=', 'sincro_data_base.server')]).id

        for server in self:
            cron_name = 'Cron of sincro_data_base: %s (%s)' % (server.name, server.id)
            existed_cron = cron_env.search(
                ['|', ('active', '=', False), ('active', '=', True), ('name', '=', cron_name)])

            if not existed_cron:
                existed_cron = existed_cron.create({
                    'name': cron_name,
                    'model_id': env_id,
                    'interval_number': server.interval_minutes,
                    'interval_type': 'minutes',
                    'numbercall': -1,
                    'state': 'code',
                    'active': False,
                    'code': 'model.browse(%s).with_context(email_error=True).action_retrieve_data()' % self.id
                })
            # creamos la action y la view con la cual se añade  un boton a la vista tipo form

            act_window_env = self.env["ir.actions.act_window"].sudo()
            view_env = self.env["ir.ui.view"].sudo()

            act_window_id = act_window_env.search(
                [('sync_id', '=', '%s.form.sync_from_ws.action' % server.model_id.model)], limit=1)
            if not act_window_id:
                domain = "[('model_id', '=', %s)]" % (
                    server.model_id.id
                )
                vals_action = {
                    "name": _("Sync from WS"),
                    "sync_id": '%s.form.sync_from_ws.action' % server.model_id.model,
                    "res_model": "sincro_data_base.syncbutton.wizard",
                    "binding_model_id": server.model_id.id,
                    "domain": domain,
                    "target": 'new',
                    "view_mode": 'form',
                    "context": '{"server_id": %s}' % server.id,
                }
                act_window_id = act_window_env.create(vals_action)

            view_id = view_env.search([('sync_id', '=', '%s.form.sync_from_ws.view' % server.model_id.model)])
            if not view_id:
                base_view_model_form_id = view_env.search(
                    [('model', '=', server.model_id.model), ('type', '=', 'form'), ('mode', '=', 'primary')],
                    order='priority ASC',
                    limit=1)
                if base_view_model_form_id:
                    arch_base_xml = '<xpath expr="//button[hasclass(\'oe_stat_button\')]" position="before">' \
                                    '<button name="%s"  string="Sync from WS" type="action" class="oe_stat_button" icon="fa-refresh"/>' \
                                    '</xpath>' % act_window_id.id
                    form_xml = \
                        self.env[server.model_id.model].fields_view_get(base_view_model_form_id.id, 'form')[
                            'arch']

                    if 'oe_stat_button' not in form_xml:
                        arch_base_xml = '<xpath expr="//form/sheet/field" position="before"><div class="oe_button_box" name="button_box">' \
                                        '<button name="%s"  string="Sync from WS" type="action" class="oe_stat_button" icon="fa-refresh"/>' \
                                        '</div></xpath>' % act_window_id.id
                    vals_view = {
                        "name": _("Sync from WS"),
                        "sync_id": '%s.form.sync_from_ws.view' % server.model_id.model,
                        "type": "form",
                        "model": server.model_id.model,
                        "inherit_id": base_view_model_form_id.id,
                        "mode": "extension",
                        "model_data_id": server.model_id.id,
                        "arch_base": arch_base_xml
                    }
                    view_id = view_env.create(vals_view)

            server.write(
                {"state": "subscribed", "cron_id": existed_cron.id, "view_id": view_id,
                 "act_window_id": act_window_id.id})

        return True

    def unsubscribe(self):
        for server in self:
            cron_item = server.cron_id
            if cron_item:
                cron_item.write({'active': False})

            act_window_env = self.env["ir.actions.act_window"].sudo()
            view_env = self.env["ir.ui.view"].sudo()

            active_server_ids = self.env['sincro_data_base.server'].search(
                [('state', '=', 'subscribed'), ('model_name', '=', server.model_id.model),
                 ('id', 'not in', server.ids)])

            if not active_server_ids:
                act_window_env.search(
                    [('sync_id', '=', '%s.form.sync_from_ws.action' % server.model_id.model)]).unlink()
                view_env.search([('sync_id', '=', '%s.form.sync_from_ws.view' % server.model_id.model)]).unlink()

            server.write({"state": "draft"})
        return True

    def get_data_from_array(self, value, path, type):
        aux_value = value
        for level in path:
            if level in aux_value:
                aux_value = aux_value[level]
            else:
                aux_value = ''

        aux_value = str(aux_value)
        if type in ['integer', 'many2one', 'many2many', 'one2many'] and aux_value == 'False':
            return ''

        if type in ['date', 'datetime']:
            # son segundos:
            if isinstance(aux_value, int):
                aux_value = datetime.fromtimestamp(aux_value).strftime("%Y-%m-%d")
            # formato "2020-04-08T04:07:08.947Z"
            else:
                aux_value = aux_value.split('T')[0]
        elif type == 'boolean':
            aux_value = str(aux_value).lower() in ('true', '1')

        return aux_value

    def _get_json_data(self, data, selected_fields, odoo_model=False):
        res = {}
        # tomo solo los fields que tengan un field_id asociado
        for mapped_field in selected_fields.filtered(lambda x: x.field_id):
            mapped_field_data = mapped_field.json_key
            if odoo_model:
                mapped_field_data = mapped_field['field_id'].name

            field_type = mapped_field.field_id.ttype
            # is_date = mapped_field.field_id.ttype in ['date', 'datetime'] or False
            # si es un Many2One lo bucamos y tomamos su id de lo contrario ponemos False
            if mapped_field.key_field_id:
                if mapped_field_data == 'static_value':
                    res[mapped_field.field_id.name] = self.env[mapped_field.field_model_id].search(
                        [(mapped_field.key_field_id.name, '=', mapped_field.default_value)]).id
                else:
                    aux_value = self.get_data_from_array(data, mapped_field_data.split('/'), field_type)
                    if aux_value:
                        aux_data = self.env[mapped_field.field_model_id].search(
                            [(mapped_field.key_field_id.name, '=', aux_value)])
                        # hay que seguir pensando sobre como asignaarle mas de una condicion
                        res[mapped_field.field_id.name] = aux_data.ids[0] if len(aux_data.ids) > 0 else False

                        # if field_type in ['many2many', 'one2many']:
                        #     # se forzara la sobreescritura del campo
                        #     if mapped_field.is_force_overwrite:
                        #         res[mapped_field.field_id.name] = [(6, 0, [int(res[mapped_field.field_id.name])])]
                        #     # solo se añadira otra info mas
                        #     else:
                        #         res[mapped_field.field_id.name] = [(4, int(res[mapped_field.field_id.name]))]
                        # [(mapped_field.key_field_id.name, '=', data[mapped_field.json_key])]).id
                        # damos el valor por defecto si existiera
                        if not res[mapped_field.field_id.name] and mapped_field.default_value:
                            res[mapped_field.field_id.name] = int(mapped_field.default_value)
            else:
                # es una valor por defecto
                if mapped_field_data == 'static_value':
                    res[mapped_field.field_id.name] = mapped_field.default_value
                # se toma el valor del campo correspondiente
                else:
                    # aux_value = self.get_data_from_array(data, mapped_field_data.split('/'),
                    #                                      field_type)
                    # if mapped_field.concat_value:
                    #     aux_value = mapped_field.concat_value % (aux_value)
                    #
                    # res[mapped_field.field_id.name] = aux_value
                    aux_val = res[mapped_field.field_id.name] = self.get_data_from_array(data,
                                                                                         mapped_field_data.split('/'),
                                                                                         field_type)

                    if mapped_field.concat_value:
                        aux_val = mapped_field.concat_value % aux_val
                    if mapped_field.is_an_img_from_url:
                        rq = requests.get(str(aux_val).strip())
                        if rq.status_code != 200:
                            res[mapped_field.field_id.name] = False
                        else:
                            res[mapped_field.field_id.name] = base64.b64encode(
                                rq.content).replace(b'\n', b'')
                    else:
                        res[mapped_field.field_id.name] = aux_val

                # damos el valor por defecto si existiera
                if not res[mapped_field.field_id.name] and mapped_field.default_value:
                    res[mapped_field.field_id.name] = mapped_field.default_value

                    # res[mapped_field.field_id.name] = data[mapped_field.json_key]
        return res

    def _check_conditional_value(self, data, conditional_values):
        for value in conditional_values:
            if (value.json_key not in data) or str(data[value.json_key]).lower() != str(
                    value.conditional_value).lower():
                return False
        return True

    def _check_same_info(self, json_main, json_inner):
        for key, value in json_inner.items():
            if key not in json_main.keys() or str(json_main[key]) != str(json_inner[key]) :
                return False
        return True

    # def _check_conditional_value(self, data, conditional_values):
    #     for value in conditional_values:
    #         if (value.json_key not in data) or str(data[value.json_key]).lower() != str(
    #                 value.conditional_value).lower():
    #             return False
    #     return True

    def _update_cascade_data(self, model_name, active_ids):
        for model_id in active_ids:
            model_item = self.env[model_name].browse(model_id)
            active_server_ids = self.env['sincro_data_base.server'].search(
                [('state', '=', 'subscribed'), ('model_name', '=', model_name)])
            for server in active_server_ids:
                headers = {}
                for header in server.api_header_ids:
                    headers[header.name] = header.value

                json_keys = {}
                for itm in server.ws_odoo_field_keys:
                    json_keys[itm.json_key] = model_item[itm.field_id.name]

                server.update_data_ws_odoo(headers, json_keys)

    def update_data_ws_odoo(self, headers, json_keys_from_views=False):
        for server in self:
            self.ensure_one()
            env_log = server.env['sincro_data_base.log']
            res = self._send_request(server.computed_path, server.ws_method, headers, '{}')
            # data = json.loads(res.text)['results']
            data = json.loads(res.text)
            # la data esta en un nivel inferior como el webservice de FACTS
            if server.key_json_data and server.key_json_data in data:
                data = data[server.key_json_data]

            conditional_values = server.mapped_fields.filtered(lambda x: x.conditional_value)
            mapped_ids = []
            env_data = self.env[server.model_id.model].sudo()
            # json_key_name = self.mapped_fields.filtered(lambda x: x.field_id.name == server.ws_odoo_field_key.name)[
            #     0].json_key
            # json_keys_data = self.mapped_fields.filtered(
            #     lambda x: x.field_id.name in server.ws_odoo_field_keys.mapped(lambda x: x.name))
            # json_keys_data = self.ws_odoo_field_keys.mapped(lambda x:x.json_key)

            if json_keys_from_views:
                filtered_data = list(filter(lambda x: self._check_same_info(x, json_keys_from_views), data))
                data = filtered_data
            new_values = []
            for idx, item in enumerate(data):
                _logger.info('Processing update server: %s, model:%s --> %s/%s' % (
                server.name, server.model_id.model, idx + 1, len(data)))

                if not self._check_conditional_value(item, conditional_values):
                    pass

                data_item = self._get_json_data(item, server.mapped_fields.filtered(lambda x: x.is_active))

                # comprobamos que existen fields en casacada para actualizarlos antes del propio objeto
                if server.ws_odoo_cascade_keys:
                    for cascade_field in server.ws_odoo_cascade_keys:
                        self._update_cascade_data(cascade_field.key_field_id.model_id.model,
                                                  [data_item[cascade_field.field_id.name]])

                json_keys = []
                for itm in self.ws_odoo_field_keys:
                    json_keys.append((itm.field_id.name,
                                      'in' if itm.field_id.ttype in ['many2many', 'one2many'] else '=',
                                      [data_item[itm.field_id.name]] if itm.field_id.ttype in ['many2many',
                                                                                               'one2many'] else
                                      data_item[itm.field_id.name]))

                # damos el formato correcto a los campos con tipo one2many or many2many
                for mapped_field in self.mapped_fields.filtered(lambda x: x.field_id):
                    if mapped_field.field_id.ttype in ['many2many', 'one2many']:
                        # se forzara la sobreescritura del campo
                        # if mapped_field.is_force_overwrite:
                        #     data_item[mapped_field.field_id.name] = [(6, 0, [int(data_item[mapped_field.field_id.name])])]
                        # # solo se añadira otra info mas
                        # else:
                        #     data_item[mapped_field.field_id.name] = [(4, int(data_item[mapped_field.field_id.name]))]
                        data_item[mapped_field.field_id.name] = [(6, 0, [int(data_item[mapped_field.field_id.name])])]

                # existed_item = env_data.search([(server.ws_odoo_field_key.name, '=', item[json_key_name])])
                existed_item = env_data.search(json_keys)
                # compruebo que el external id existe para actualizar de lo contrario inserto
                try:
                    if existed_item:
                        # existed_item.write(data_item) mejorar esta comprobacion
                        if not self._check_same_info(existed_item.copy_data()[0], data_item):
                            for mapped_field in self.mapped_fields.filtered(lambda x: x.field_id):
                                if mapped_field.field_id.ttype in ['many2many', 'one2many']:
                                    # se forzara la sobreescritura del campo
                                    if not mapped_field.is_force_overwrite:
                                        data_item[mapped_field.field_id.name] = [
                                            (4, int(data_item[mapped_field.field_id.name][0][2]))]

                                        # response_code = res.status_code

                            created_log = env_log.create({
                                'url': 'Update register',
                                'item_id': existed_item.id,
                                'created_date': datetime.now(),
                                'model': str(server.model_id.model),
                                'status_code': res.status_code,
                                'server_id': server.id,
                                'old_value': str(existed_item.copy_data()[0]),
                                'new_value': str(data_item)
                            })
                            self.log_ids = [(4, created_log.id)]
                            existed_item.write(data_item)
                        # if not self._get_json_data(existed_item.copy_data()[0],
                        #                            server.mapped_fields.filtered(lambda x: x.is_active),
                        #                            True) == data_item:

                    # inserto nuevo registro
                    else:
                        item_id = env_data.create(data_item)
                        created_log = env_log.create({
                            'url': 'New register',
                            'item_id': item_id,
                            'created_date': datetime.now(),
                            'model': str(server.model_id.model),
                            'server_id': server.id,
                            'new_value': str(data_item)
                        })
                        self.log_ids = [(4, created_log.id)]
                except Exception as e:
                    pass

            # env_data.create(new_values)

    #
    # queda desarrollar esta parte
    def update_data_odoo_ws(self, headers):
        for server in self:
            self.ensure_one()

    def action_retrieve_data(self, *args):

        env_id = self.env['ir.model'].search([('model', '=', 'sincro_data_base.server')]).id
        for server in self:
            self.ensure_one()
            error_msgs = {}
            headers = {}
            for header in server.api_header_ids:
                headers[header.name] = header.value

            if server.method == 'ws_odoo':
                return self.update_data_ws_odoo(headers)

            if server.method == 'odoo_ws':
                return self.update_data_ws_odoo(headers)

            aux_domain = safe_eval(server.domain or "[]")
            env_aux = server.env[server.model_id.model]

            filtered_items = env_aux.search(aux_domain)

            for item in filtered_items:
                computed_path = server.api_base_url + server.path % tuple(
                    reversed(tuple(map(lambda value: env_aux.browse([item.id])[
                        value.field_value.name] if value.type != 'constant' else value.constant_value,
                                       server.parameter_ids))))

                compute_json_data = server.json_configuration_id.get_json(server.json_configuration_id,
                                                                          env_aux.browse(
                                                                              [item.id]),
                                                                          server.json_pretty)

                res = server._send_request(computed_path, server.method, headers, compute_json_data)

                env_log = server.env['sincro_data_base.log']
                # response_code = res.status_code
                created_log = env_log.create({
                    'url': computed_path,
                    'item_id': item.id,
                    'created_date': datetime.now(),
                    'model': str(env_id),
                    'status_code': res.status_code,
                    'server_id': self.id,
                    'request': str(res.request.body),
                    'response': res.text
                })
                self.log_ids = [(4, created_log.id)]

            server.retrieve_date = datetime.now()

    def _send_request(self, url, method, headers, body):
        self.ensure_one()
        return requests.request(method, url, headers=headers, json=json.loads(body), verify=False)

    def _save_in_log(self, server, url, created_date, server_id, model='', item_id=-1, status_code='', request='',
                     response='', method=''):
        env_log = self.env['sincro_data_base.log']
        server.retrieve_date = datetime.now()
        created_log = env_log.create({
            'url': url,
            'item_id': item_id,
            'created_date': created_date,
            'model': str(model),
            'method': method,
            'server_id': server_id,
            'status_code': status_code,
            'request': str(request),
            'response': str(response)
        })
        self.log_ids = [(4, created_log.id)]

    # def _send_request(self, url, method, headers):
    #     self.ensure_one()
    #     return requests.request(method, url, headers=headers)
