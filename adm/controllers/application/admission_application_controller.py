# -*- coding: utf-8 -*-
import werkzeug

from odoo import http, api, SUPERUSER_ID, exceptions, _
from odoo.http import request, Response
from odoo.tools import safe_eval

from odoo.addons.adm.controllers.admission_controller import AdmissionController

import base64
import logging
import hashlib

_logger = logging.getLogger(__name__)


class ApplicationController(AdmissionController):

    @http.route('/admission/application/<model(adm.application):application_id>/invite/<model(adm.application.invitation):invitation_id>/<string:secure_hash>',
                website=True, methods=['GET'])
    def invite_partner_to_application(self, application_id, invitation_id,
                                      secure_hash, **params):
        salt = invitation_id.salt
        to_email = request.env.user.email
        text_to_hash = '%s%i-%s' % (salt, application_id, to_email)
        hash_to_compare = hashlib.sha256(
            text_to_hash.encode('utf-8')).hexdigest()

        if hash_to_compare != secure_hash:
            raise exceptions.AccessError(_("Ensure to copy the url as you get it"))

        return http.request.render('adm.template_application_invite_partner', {
            "application_id": application_id,
            "request": request,
            "invitation_id": invitation_id.sudo(),
            "user": http.request.env.user,
            })

    @http.route('/admission/application/<model(adm.application):application_id>/invite/<model(adm.application.invitation):invitation_id>/<string:secure_hash>',
                website=True, methods=['POST'], csrf=True)
    def do_invitation(self, application_id, invitation_id,
                      secure_hash, **params):

        # Check again, just for security
        salt = invitation_id.salt
        to_email = request.env.user.email
        text_to_hash = '%s%i-%s' % (salt, application_id, to_email)
        hash_to_compare = hashlib.sha256(
            text_to_hash.encode('utf-8')).hexdigest()

        if hash_to_compare != secure_hash:
            raise exceptions.AccessError(_("Ensure to copy the url as you get it"))
        if invitation_id.state:
            raise exceptions.UserError(_("Invitation already solved"))

        invitation_id.access_family_id = int(params['family_id'])
        if not invitation_id.invited_user_id:
            invitation_id.invited_user_id = request.env.user

        invitation_id.state = params.get('state', 'rejected')
        return request.redirect('/admission/applications/%i' % application_id.id)

    @http.route("/admission/family/create", methods=['POST'], csrf=True)
    def create_family(self, **params):
        parent = request.env.user.partner_id.sudo()

        family_name = params.get('family_name', 'Family of %s' % parent.name)

        family = request.env['res.partner'].sudo().create({
            'name': family_name,
            'is_family': True,
            'is_company': True,
            'member_ids': [(4, parent.id, False)]
            })
        parent.write({
            'family_ids': [(4, family.id, False)]
            })

        return Response(str(family.id), status=200)

    @http.route("/admission/applications/create", auth="public",
                methods=["GET"], website=True, csrf=False)
    def show_create_application_form(self, **params):
        ApplicationEnv = http.request.env['adm.application']

        countries = request.env['res.country'].sudo().search([])
        genders = request.env['adm.gender'].sudo().search([])
        languages = request.env['adm.language'].sudo().search([])

        grade_levels = (request.env['school_base.grade_level'].sudo()
                        .search([('active_admissions', '=', True)]))
        school_years = (request.env['school_base.school_year'].sudo()
                        .search([('active_admissions', '=', True)]))
        companies = (http.request.env['res.company'].sudo()
                     .search([('country_id', '!=', False)]))

        template = "adm.template_application_create_application"

        return http.request.render(template, {
            "application_id": ApplicationEnv,
            "countries": countries,
            "student_photo": "data:image/png;base64",
            "adm_languages": languages,
            "genders": genders,
            "grade_levels": grade_levels,
            "school_years": school_years,
            "create_mode": True,
            "create_grade_level": params.get("grade_level"),
            "company": companies and companies[0],
            })

    @http.route("/admission/applications/create", auth="public",
                methods=["POST"], website=True, csrf=False)
    def create_application(self, **params):

        env = api.Environment(request.env.cr, SUPERUSER_ID,
                              request.env.context)

        PartnerEnv = env["res.partner"]
        ApplicationEnv = env["adm.application"]

        field_ids = env.ref("adm.model_adm_application").field_id
        fields = [field_id.name for field_id in field_ids]
        keys = params.keys() & fields
        result = {k: params[k] for k in keys}
        field_types = {field_id.name: field_id.ttype for field_id in field_ids}

        many2one_fields = [name for name, value in field_types.items() if
                           value == "many2one"]

        for key in result.keys():
            if key in many2one_fields:
                result[key] = int(result.get(key, False) or False)
                if result[key] == -1:
                    result[key] = False
                    pass

        user_id = http.request.env.user
        parent = user_id.partner_id

        family_id = int(result.pop("family_id", False) or False)
        family = env['res.partner'].browse(family_id)

        if not family:
            family = PartnerEnv.create({
                'name': 'Family of %s' % parent.name,
                'is_family': True,
                'is_company': True,
                'member_ids': [(4, parent.id, False)]
                })
            family_id = family.id
            # result["family_id"] = family_id
            parent.write({
                'family_ids': [(4, family.id, False)]
                })

        # noinspection PyUnresolvedReferences
        partner = PartnerEnv.create({
            "first_name": result.get("first_name"),
            "middle_name": result.get("middle_name"),
            "last_name": result.get("last_name"),
            "image_1920": params.get("file_upload") and base64.b64encode(
                params["file_upload"].stream.read()),
            "parent_id": family.id,
            "person_type": "student",
            "family_ids": [(4, family.id, False)],
            })
        family.write({
            'member_ids': [(4, partner.id, False)]
            })
        application = ApplicationEnv.create({
            "first_name": result.get("first_name"),
            "middle_name": result.get("middle_name"),
            "last_name": result.get("last_name"),
            "family_id": family_id,
            "partner_id": partner.id,
            "responsible_user_id": request.env.user.id,
            "responsible_user_ids": [(4, request.env.user.id, 0)],
            })
        # result["relationship_ids"] = [(0, 0, {
        #     "partner_relation_id": parent.id,
        #     "family_id": family_id,
        #     })]
        application.write(result)

        # Send pending family emails
        invite_mail_json_list = safe_eval(params.get('invite_mail_json_list', '[]'))

        for invite_mail_json in invite_mail_json_list:
            email_to = invite_mail_json['email']
            # access = invite_mail_json['access']
            access = []

            mail_template = request.env.company.sudo()\
                .mail_inviting_partner_to_application_id
            invitation = application\
                .with_user(request.env.user.id)\
                .get_partner_invitation(
                    email=email_to, access=access, mail_template=mail_template)
        return (http.request
                .redirect("/admission/applications/%s" % application.id))

    @http.route("/admission/applications/"
                "<model(adm.application):application_id>/check", auth="public",
                methods=["POST"], website=True, csrf=False)
    def check_application(self, application_id, **params):

        # if len(self.getPendingTasks(application_id)) == 0:
        # BUSCAMOS EL STATUS QUE SEA DE TIPO SUBMITTED PARA TRANSLADAR
        # LA PETICION DEL USUARIO
        StatusEnv = request.env["adm.application.status"].sudo()
        status_submitted = StatusEnv.search([('type_id', '=', 'submitted')])[0]
        if status_submitted:
            application_id.sudo().force_status_submitted(status_submitted.id)

        return request.redirect(
            http.request.httprequest.referrer + "?checkData=1")

    #####################
    # Application Pages #
    #####################
    @http.route("/admission/applications/"
                "<model(adm.application):application_id>/", auth="public",
                methods=["GET"], website=True, csrf=False)
    def see_application(self, application_id, **params):
        return request.render("adm.template_application_menu_instructions",
                              self.compute_view_render_params(application_id))

    @http.route("/admission/applications", auth="public", methods=["GET"],
                website=True)
    def admission_list(self, **params):

        # obtenemos todos los registros de reenrollment en las cuales el
        # estudiante asociado este relacionado mediante la familia con el
        # user que esta accediendo dede el portal.
        application_ids = request.env.user.application_ids
        response = http.request.render(
            "adm.template_admission_application_list", {
                "application_ids": application_ids,
                })
        return response

    @http.route('/admission/applications/'
                '<model(adm.application):application_id>/<path:page_path>',
                methods=["GET"], website=True, strict_slashes=False)
    def generic_page_controller(self, application_id, page_path, **params):
        page = request.env['adm.application.page'].search([('url', '=', page_path)])
        page_params = self.compute_view_render_params(application_id)
        if not page.view_template_id:
            raise werkzeug.exceptions.NotFound()
        page_params.update({
            'page_id': page
            })
        return page.view_template_id.render(page_params)
