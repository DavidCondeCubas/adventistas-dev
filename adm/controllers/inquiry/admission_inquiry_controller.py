# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.adm.utils import formatting
import base64

import logging


def get_parameters():
    return http.request.httprequest.args


def post_parameters():
    return http.request.httprequest.form

logger = logging.getLogger(__name__)

class InquiryController(http.Controller):

    # ===================================================================================================================
    # @http.route("/")
    # def
    # ===================================================================================================================

    @http.route("/admission/inquiry", auth="public", methods=["GET"],
                website=True)
    def admission_web(self, **params):
        countries = http.request.env['res.country'].sudo()
        states = http.request.env['res.country.state'].sudo()
        sources = http.request.env['adm.inquiry.source'].sudo()
        contact_times = http.request.env['adm.contact_time']
        degree_programs = http.request.env['adm.degree_program']

        grade_level = http.request.env['school_base.grade_level']
        school_year = http.request.env['school_base.school_year']
        service = http.request.env['school_base.service'].sudo()
        gender_env = http.request.env['school_base.gender'].sudo()
        relationship_type_env = http.request.env['school_base.relationship_type'].sudo()

        LanguageEnv = http.request.env["adm.language"]
        languages = LanguageEnv.browse(LanguageEnv.search([])).ids

        family_id = -1

        if 'family_id' in params:
            family_id = params['family_id']

        website_id = http.request.env.context.get('website_id', False)
        website_id = http.request.env['website'].sudo().browse(website_id)

        companies = http.request.env['res.company'].sudo().search(
            [('country_id', '!=', False)])
        response = http.request.render('adm.template_admission_inquiry', {
            'grade_levels': website_id.company_id.school_code_ids.mapped('grade_level_ids'),
            'school_years': school_year.search(
                [('active_admissions', '=', True)]),
            'services': service.search([]),
            'sources': sources.search([]),
            'countries': countries.search([]),
            'states': states.search([]),
            'gender': gender_env.search([]),
            'check_family_id': True,
            'family_name': '',
            'family_id': family_id,
            'relationship_types': relationship_type_env.search([]),
            "adm_languages": languages,
            'company': companies and companies[0],
            })
        return response

    def all_exist(avalue, bvalue):
        return all(any(x in y for y in bvalue) for x in avalue)

    @http.route("/admission/inquiry", auth="public", methods=["POST"],
                website=True, csrf=False)
    def add_inquiry(self, **params):

        PartnerEnv = http.request.env['res.partner']

        if "txtMiddleName_1" not in params:
            params["txtMiddleName_1"] = ""

        if "txtRelatedNames" not in params:
            params["txtRelatedNames"] = ""

        source_id = False
        if "selSource" in params:
            source_id = int(params["selSource"])

        other_source = False
        if "txtOtherSource" in params:
            other_source = params["txtOtherSource"]

        known_people_in_school = params["txtRelatedNames"]

        if 'checkbox_family_id' in params and params[
            "checkbox_family_id"] == 'on':
            family_id_fact = params["input_family_id"]
            if len(PartnerEnv.sudo().search([('facts_id', '=', family_id_fact),
                                             ('is_family', '=', True)])) == 0:
                countries = http.request.env['res.country']
                states = http.request.env['res.country.state']
                contact_times = http.request.env['adm.contact_time']
                degree_programs = http.request.env['adm.degree_program']
                grade_level = http.request.env['school_base.grade_level']
                school_year = http.request.env['school_base.school_year']
                service = http.request.env['school_base.service'].sudo()

                response = http.request.render(
                    'adm.template_admission_inquiry', {
                        'grade_levels': grade_level.search(
                            [('active_admissions', '=', True)]),
                        'school_years': school_year.search([]),
                        'services': service.search([]),
                        'countries': countries.search([]),
                        'states': states.search([]),
                        'sources_id': source_id,
                        'check_family_id': False,
                        'family_name': '',
                        'parent': False,
                        })
                return response
            else:
                # PARA TOMAR POR FACTS ID
                #   family_data = PartnerEnv.sudo().search([('facts_id','=',family_id_fact),('is_family', '=', True)])[0]
                # CASO DE TOMAR POR EL FACTS UD ID
                family_data = PartnerEnv.sudo().search(
                    [('facts_id', '=', family_id_fact),
                     ('is_family', '=', True)])[0]
                family_id = family_data
                mobile_1 = family_data.mobile
                email_1 = family_data.email
                country_id = family_data.country_id.id
                parents_ids_created = (family_data.member_ids.filtered(
                    lambda item: item.function == 'parent')).ids

        else:
            # Create a new family
            full_name = "{}, {}{}".format(params["txtLastName_1"],
                                          params["txtFirstName_1"],
                                          "" if not params[
                                              "txtMiddleName_1"] else " {}".format(
                                              params["txtMiddleName_1"]))

            first_name = params["txtFirstName_1"]
            middle_name = params["txtMiddleName_1"]
            last_name = params["txtLastName_1"]
            citizenship_1 = int(params["selCountry_1"])

            # Family address
            country_id = int(params["selCountry"])
            state_id = int(params.get("selState", False)) or False
            city = params["txtCity"]
            zip = params.get("txtZip", False)

            mobile_1 = params["txtCellPhone_1"]
            email_1 = params["txtEmail_1"]

            financial_responsability_1 = params.get(
                "txtFinancialResponsability_1", False)
            financial_responsability_2 = params.get(
                "txtFinancialResponsability_2", False)

            invoice_address_1 = params.get("txtInvoiceAddress_1", False)
            invoice_address_2 = params.get("txtInvoiceAddress_2", False)
            street_address_1 = params.get("txtStreetAddress", False)
            street_address_2 = params.get("txtStreetAddress2", False)

            family_1 = ''
            if 'selFamily_1' in params:
                family_1 = params["selFamily_1"]

            partner_body = {
                "name": "{} family".format(last_name),
                "company_type": "company",
                "is_family": True,
                'mobile': mobile_1,
                'home_address_ids': [(0, 0, {
                    'street': street_address_1,
                    'street2': street_address_2,
                    'city': city,
                    'zip': zip,
                    'country_id': country_id,
                    'state_id': state_id
                    })]
                }

            if family_1 is '':
                family_id = PartnerEnv.sudo().create(partner_body)
                home_address_id = family_id.home_address_ids[0]
                parent_id_1 = PartnerEnv.sudo().create({
                    "name": full_name,
                    "first_name": first_name,
                    "middle_name": middle_name,
                    "last_name": last_name,
                    "parent_id": family_id.id,
                    "function": "parent",
                    "family_ids": [(6, 0, [family_id.id])],
                    "citizenship": citizenship_1,
                    'mobile': mobile_1,
                    'email': email_1,
                    'street': street_address_1,
                    'street2': street_address_2,
                    'home_address_id': home_address_id.id
                    })
            else:
                family_id = PartnerEnv.sudo().search([('id', '=', family_1)])
                parent_id_1 = PartnerEnv.sudo().search(
                    [('email', '=', email_1), ('function', '=', 'parent')])[0]

            parents_ids_created = []
            family_write_data = {
                "member_ids": [],
                "financial_res_ids": [],
                "invoice_address_id": False
                }
            family_write_data["member_ids"].append((4, parent_id_1.id))
            # family_id.write({'member_ids': [(4,parent_id_1.id)]})
            if financial_responsability_1:
                family_write_data["financial_res_ids"].append(
                    (4, parent_id_1.id))
            if invoice_address_1:
                family_write_data["invoice_address_id"] = parent_id_1.id

            parents_ids_created.append(parent_id_1.id)

            if "txtMiddleName_2" not in params:
                params["txtMiddleName_2"] = ""

            if all(k in params for k in (
                "txtFirstName_2", "txtLastName_2", "selCountry_2",
                "txtCellPhone_2", "txtEmail_2")):
                first_name = params["txtFirstName_2"]
                middle_name = params["txtMiddleName_2"]
                last_name = params["txtLastName_2"]
                citizenship_2 = int(params["selCountry_2"])
                full_name = "{}, {}{}".format(params["txtLastName_2"],
                                              params["txtFirstName_2"],
                                              "" if not params[
                                                  "txtMiddleName_2"] else " {}".format(
                                                  params["txtMiddleName_2"]))
                mobile_2 = params["txtCellPhone_2"]
                email_2 = params["txtEmail_2"]

                if len(PartnerEnv.sudo().search([('email', '=', email_2), (
                'function', '=', 'parent')])) > 0:
                    parent_id_2 = PartnerEnv.sudo().search(
                        [('email', '=', email_2),
                         ('function', '=', 'parent')])[0]
                    parent_id_2.write({
                                          'family_ids': [(4, family_id.id)]
                                          })
                else:
                    parent_id_2 = PartnerEnv.sudo().create({
                        "name": full_name,
                        "first_name": first_name,
                        "middle_name": middle_name,
                        "last_name": last_name,
                        "parent_id": family_id.id,
                        "function": "parent",
                        "family_ids": [(6, 0, [family_id.id])],
                        "citizenship": citizenship_2,
                        'mobile': mobile_2,
                        'email': email_2,
                        'home_address_id': home_address_id.id
                        })

                parents_ids_created.append(parent_id_2.id)
                # family_id.write({'member_ids': [(4, parent_id_2.id)]})
                family_write_data["member_ids"].append((4, parent_id_2.id))
                if financial_responsability_2:
                    family_write_data["financial_res_ids"].append(
                        (4, parent_id_2.id))
                if invoice_address_2:
                    family_write_data["invoice_address_id"] = parent_id_2.id

            family_id.write(family_write_data)

        # Create students
        id_students = list()
        students_total = int(params["studentsCount"])
        if 'service_count' in params:
            service_count = 1  # int(params["service_count"])

        first_name_list = post_parameters().getlist("txtStudentFirstName")
        last_name_list = post_parameters().getlist("txtStudentLastName")
        middle_name_list = post_parameters().getlist("txtStudentMiddleName")
        birthday_list = post_parameters().getlist("txtStudentBirthday")
        gender_list = post_parameters().getlist("selStudentGender")

        interest_grade_level_list = post_parameters().getlist(
            "selStudentInterestGradeLevel")
        current_school_code_list = post_parameters().getlist(
            "selStudentSchoolCode")
        current_school_year_list = post_parameters().getlist(
            "selStudentSchoolYear")

        InquiryEnv = http.request.env["adm.inquiry"]

        for index_student in range(students_total):
            first_name = first_name_list[index_student]
            middle_name = middle_name_list[index_student]
            last_name = last_name_list[index_student]
            birthday = birthday_list[index_student]
            gender = gender_list[index_student]
            interest_grade_level = interest_grade_level_list[index_student]
            current_school_code = current_school_code_list[index_student]
            current_school_year = current_school_year_list[index_student]
            full_name_student = "{}, {}{}".format(last_name, first_name,
                                                  "" if not middle_name else " {}".format(
                                                      middle_name))
            service_ids = []
            for service in post_parameters().getlist(
                    "txtStudent%sExtraServices" % index_student):
                if service:
                    service_ids.append(int(service))
            family_res_finance = []
            for category_id in http.request.env[
                'product.category'].sudo().search([('parent_id', '=', False)]):
                family_res_finance.append((0, 0, {
                    'family_id': family_id.id,
                    'category_id': category_id.id,
                    'percent': 100
                    }))
            school_code_id = current_school_code and int(current_school_code) or False
            school_year_id = current_school_year and int(current_school_year) or False
            grade_level_id = interest_grade_level and int(interest_grade_level) or False
            student_id = PartnerEnv.sudo().create({
                "name": full_name_student,
                "first_name": first_name,
                "middle_name": middle_name,
                "last_name": last_name,
                "function": "student",
                "person_type": "student",
                'school_code_ids': [(4, school_code_id, False)],
                'school_grade_ids': [(0, 0, {
                    'school_code_id': school_code_id,
                    'grade_level_id': grade_level_id,
                    })],
                'enrollment_history_ids': [(0, 0, {
                    'school_code_id': school_code_id,
                    'grade_level_id': grade_level_id,
                    'school_year_id': school_year_id,
                    'note': "Created by inquiry process",
                    })],
                "family_ids": [(6, 0, family_id.ids)],
                'date_of_birth': birthday,
                'gender': gender and int(gender) or False,
                'mobile': mobile_1,
                'family_res_finance_ids': family_res_finance,
                'home_address_id': home_address_id.id,
                })
            family_id.write({'member_ids': [(4, student_id.id)]})

            try:
                family_id.set_member_relationship(
                    individual_id=student_id.id,
                    relation_id=parent_id_1.id,
                    reltype_id=int(params.get('selRelationshipType_1', False) or False))
            except NameError as e:
                logger.warning("Parent 1 is not set")

            try:
                family_id.set_member_relationship(
                    individual_id=student_id.id,
                    relation_id=parent_id_2.id,
                    reltype_id=int(params.get('selRelationshipType_2', False) or False))
            except NameError as e:
                logger.warning("Parent 2 is not set")

            # Create an inquiry for each new student
            new_inquiry = InquiryEnv.sudo().create({
                "partner_id": student_id.id,
                'first_name': first_name,
                'middle_name': middle_name,
                'last_name': last_name,
                #                 'current_grade_level_id': current_grade_level and int(current_grade_level) or False,
                'grade_level_id': grade_level_id,
                'school_year_id': school_year_id,
                'responsible_id': [(6, 0, parents_ids_created)],
                'sources_id': source_id,
                'source_other': other_source,
                'known_people_in_school': known_people_in_school
                })

            student_id.inquiry_id = new_inquiry.id
            id_students.append(student_id)

            if params.get("message"):
                new_inquiry.message_post(
                    body="Message/Question: %s" % params["message"])

        response = http.request.render('adm.template_inquiry_sent')
        return response

