from odoo import models, api, fields


class SyncButton(models.TransientModel):
    _name = 'sincro_data_base.syncbutton.wizard'

    def sync_data(self):
        model_name = self._context['active_model'] or False
        active_ids = self._context['active_ids']
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
                    # json_keys.append((itm.field_id.name,
                    #                   'in' if itm.field_id.ttype in ['many2many', 'one2many'] else '=',
                    #                   [model_item[itm.field_id.name]] if itm.field_id.ttype in ['many2many',
                    #                                                                             'one2many'] else
                    #                   model_item[itm.field_id.name]))

                server.update_data_ws_odoo(headers, json_keys)
