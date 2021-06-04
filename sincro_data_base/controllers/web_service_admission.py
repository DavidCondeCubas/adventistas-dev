import json

# from formiodata.components import selectboxesComponent

from odoo import http
import datetime
import logging
import re
from odoo.tools.safe_eval import safe_eval

# Se añaden campos:
# - Siblings
# - Datos de los hermanos
# - Horario de partner
# - Comment en res.parthner

# Updated 2020/12/14
# By Luis
# Just some clean up
_logger = logging.getLogger(__name__)


class WebServiceController(http.Controller):
    """ Controlador encargado de devolver datos de las admisiones,
    para insertarlas en FACTS
    """

    @http.route("/sincro_data_base/getData", auth="public", methods=["GET"], cors='*')
    def getAdmissions(self, **params):

        """ Definiendo la url desde donde va ser posible acceder, tipo de
        metodo,
        cors para habiltiar accesos a ip externas.
        """

        allowed_urls = (http.request.env['ir.config_parameter'].sudo()
                        .get_param('allow_urls', ''))

        # permite acceder desde cualquier url sin realizar comprobaciones:
        mode_testing = (http.request.env['ir.config_parameter'].sudo()
                        .get_param('sincro_data_base_ws_open', False))

        if not str(mode_testing).lower() in ('true','1'):
            origin_url = '-1'
            if ('HTTP_ORIGIN' in http.request.httprequest.headers.environ):
                origin_url = http.request.httprequest.headers.environ['HTTP_ORIGIN']

            if (origin_url is '-1' or origin_url not in allowed_urls):
                return 'Denied access'


        # toammaos el parametro de la url
        param_config = params['config_name']
        selected_config = http.request.env['sincro_data_base.webservice_configurator'].search(
            [('name', 'like', str(param_config))])

        if not selected_config:
            return 'The webservice configurator %s not found ' % str(param_config)

        domain_data = safe_eval(selected_config.domain or "[]")
        data_items = http.request.env[selected_config.sudo().model_id.model].sudo().search(domain_data)

        json_aux_res = '{"%s": [' % selected_config.label
        for idx, adm_aux in enumerate(data_items):
            if idx > 0:
                json_aux_res += ','
            json_aux_res += selected_config.panel_configuration.get_json(selected_config.panel_configuration, adm_aux,
                                                                         selected_config.pretty)

        json_aux_res += ']}'

        return json_aux_res

    # @http.route("/admission/applications/change_status", auth="public", methods=["POST"],
    #             cors='*', csrf=False)
    # # define una funcion principal
    # def change_status(self, **kw):
    #     data = json.loads(kw["data"])
    #     application = http.request.env['adm.application'].sudo()
    #     application_record = application.browse(data)
    #     allowed_url = http.request.env['ir.config_parameter'].sudo().get_param('allow_urls', '')
    #     origin_url = '-1'
    #
    #     # permite acceder desde cualquier url sin realizar comprobaciones:
    #     mode_testing = (http.request.env['ir.config_parameter'].sudo()
    #                     .get_param('mode_testing_ws_open', False))
    #
    #     if not str(mode_testing).lower() in ('true', '1'):
    #         if ('HTTP_ORIGIN' in http.request.httprequest.headers.environ):
    #             origin_url = http.request.httprequest.headers.environ['HTTP_ORIGIN']
    #
    #         if (origin_url is '-1' or origin_url not in allowed_url):
    #             return 'Denied access'
    #
    #     status_id = http.request.env['adm.application.status'].sudo().search([('type_id', '=', 'import_completed')]).id
    #
    #     application_record.write({
    #         'status_id': status_id
    #     })
    #     _logger.info("application moved correctly %s to state %s" % (
    #         application_record.mapped('name'), application_record.mapped('status_type')))
    #     #         return json.dumps(data)
    #     return str(data)



