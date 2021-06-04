# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.adm.utils import formatting
import base64

from odoo.addons.adm.controllers.inquiry.admission_inquiry_controller import InquiryController


def get_parameters():
    return http.request.httprequest.args


def post_parameters():
    return http.request.httprequest.form


class AdmCustom(InquiryController):
    
    @http.route("/admission/inquiry", auth="public", methods=["POST"], website=True, csrf=False)
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

        if 'checkbox_family_id' in params:
            family_id_fact = int(params.get("input_family_id", False))
            select_family_id_type = params.get('select_family_id_type', 'facts_id')
            if select_family_id_type == 'facts_id':
                field_id_name = 'facts_id'
            elif select_family_id_type == 'odoo_id':
                field_id_name = 'id'
            family_id = PartnerEnv.sudo().search([(field_id_name, '=', family_id_fact), ('is_family', '=', True)])[:1]
            if not family_id:
                countries = http.request.env['res.country']
                states = http.request.env['res.country.state']
                contact_times = http.request.env['adm.contact_time']
                degree_programs = http.request.env['adm.degree_program']
                grade_level = http.request.env['school_base.grade_level']
                school_year = http.request.env['school_base.school_year']

                response = http.request.render('adm.template_admission_inquiry', {
                    'grade_levels': grade_level.search([('active_admissions', '=', True)]),
                    'school_years': school_year.search([]),
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
                #   family_id = PartnerEnv.sudo().search([('facts_id','=',family_id_fact),('is_family', '=', True)])[0]
                # CASO DE TOMAR POR EL FACTS UD ID
                mobile_1 = family_id.mobile
                email_1 = family_id.email
                country_id = family_id.country_id.id
                parents_ids_created = (family_id.member_ids.filtered(lambda item: item.person_type == 'parent')).ids
                home_address_id = family_id.home_address_ids[:1]

        else:
            # Create a new family
            full_name = "{}, {}{}".format(params["txtLastName_1"],
                                           params["txtFirstName_1"],
                                           "" if not params["txtMiddleName_1"] else " {}".format(params["txtMiddleName_1"]))

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
            email_1 = params.get("txtEmail_1", False)

            financial_responsability_1 = params.get("txtFinancialResponsability_1", False)
            financial_responsability_2 = params.get("txtFinancialResponsability_2", False)

            invoice_address_1 = params.get("txtInvoiceAddress_1", False)
            invoice_address_2 = params.get("txtInvoiceAddress_2", False)
            street_address_1 = params.get("txtStreetAddress", False)
            street_address_2 = params.get("txtStreetAddress2", False)

            family_1 = ''
            if 'selFamily_1' in params:
                family_1 = params["selFamily_1"]
            
            family_name =  params.get('txtFamilyName', "{} family".format(last_name))
            
            family_body = {
                    "name": family_name,
                    "company_type": "company",
                    "is_family": True,
                    'mobile': mobile_1,
                    'home_address_ids': [(0, 0,
                                      {
                                          'street': street_address_1,
                                          'street2': street_address_2,
                                          'city': city,
                                          'zip': zip,
                                          'country_id': country_id,
                                          'state_id': state_id
                                      })]
                }

            if family_1 is '':
                family_id = PartnerEnv.sudo().create(family_body)
                home_address_id = family_id.home_address_ids[0]
                parent_id_1 = PartnerEnv.sudo().create({
                    "name": full_name,
                    "first_name": first_name,
                    "middle_name": middle_name,
                    "last_name": last_name,
                    "parent_id": family_id.id,
                    "person_type": "parent",
                    "family_ids": [(6,0,[family_id.id])],
                    "citizenship": citizenship_1,
                    'mobile': mobile_1,
                    'email': email_1,
                    'street': street_address_1,
                    'street2': street_address_2,
                    'home_address_id': home_address_id.id
                })
            else:
                family_id = PartnerEnv.sudo().search([('id', '=', family_1)])
                parent_id_1 = PartnerEnv.sudo().search([('email','=',email_1),('person_type', '=', 'parent')])[0]

            parents_ids_created = []
            family_write_data = {
                "member_ids": [],
                "financial_res_ids": [],
                "invoice_address_id": False
            }
            family_write_data["member_ids"].append((4, parent_id_1.id))
            # family_id.write({'member_ids': [(4,parent_id_1.id)]})
            if financial_responsability_1:
                family_write_data["financial_res_ids"].append((4, parent_id_1.id))
            if invoice_address_1:
                family_write_data["invoice_address_id"] = parent_id_1.id

            parents_ids_created.append(parent_id_1.id)

            if "txtMiddleName_2" not in params:
                params["txtMiddleName_2"] = ""
            
            if all (k in params for k in ("txtFirstName_2", "txtLastName_2", "selCountry_2", "txtCellPhone_2","txtEmail_2")):
                first_name = params["txtFirstName_2"]
                middle_name = params["txtMiddleName_2"]
                last_name = params["txtLastName_2"]
                citizenship_2 = int(params["selCountry_2"])
                full_name = "{}, {}{}".format(params["txtLastName_2"], params["txtFirstName_2"],
                                              "" if not params["txtMiddleName_2"] else " {}".format(
                                                  params["txtMiddleName_2"]))
                mobile_2 = params["txtCellPhone_2"]
                email_2 = params.get("txtEmail_2", False)


                if len(PartnerEnv.sudo().search([('email', '=', email_2), ('person_type', '=', 'parent')])) > 0:
                    parent_id_2 = PartnerEnv.sudo().search([('email', '=', email_2), ('person_type', '=', 'parent')])[0]
                    parent_id_2.write({'family_ids': [(4,family_id.id)]})
                else:
                    parent_id_2 = PartnerEnv.sudo().create({
                        "name": full_name,
                        "first_name": first_name,
                        "middle_name": middle_name,
                        "last_name": last_name,
                        "parent_id": family_id.id,
                        "person_type": "parent",
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
                    family_write_data["financial_res_ids"].append((4, parent_id_2.id))
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

#         current_grade_level_list = post_parameters().getlist("selStudentCurrentGradeLevel")
        interest_grade_level_list = post_parameters().getlist("selStudentInterestGradeLevel")
        current_school_code_list = post_parameters().getlist("selStudentSchoolCode")
        current_school_year_list = post_parameters().getlist("selStudentSchoolYear")
        
        InquiryEnv = http.request.env["adm.inquiry"]
        for index_student in range(students_total):
            first_name = first_name_list[index_student]
            middle_name = middle_name_list[index_student]
            last_name = last_name_list[index_student]
            birthday = birthday_list[index_student]
            gender = gender_list[index_student]
#             current_grade_level = current_grade_level_list[index_student]
            interest_grade_level = interest_grade_level_list[index_student]
            current_school_code = current_school_code_list[index_student]
            current_school_year = current_school_year_list[index_student]
            full_name_student = "{}, {}{}".format(last_name, first_name, "" if not middle_name else " {}".format(middle_name))
            service_ids = []
            for service in post_parameters().getlist("txtStudent%sExtraServices" % index_student):
                if service:
                    service_ids.append(int(service))
            family_res_finance = []
            for category_id in http.request.env['product.category'].sudo().search([('parent_id', '=', False)]):
                family_res_finance.append((0,0,
                                           {
                                               'family_id': family_id.id,
                                               'category_id': category_id.id,
                                               'percent': 100
                                            }))
            school_code_id = current_school_code and int(current_school_code) or False
            interest_grade_level_id = interest_grade_level and int(interest_grade_level) or False
            id_student = PartnerEnv.sudo().create({
                "name": full_name_student,
                "first_name": first_name,
                "middle_name": middle_name,
                "last_name": last_name,
                "function": "student",
                "person_type": "student",
                'school_code_id': school_code_id,
                'school_code_ids': [(6, 0, [school_code_id])],
                'school_year_id': current_school_year and int(current_school_year) or False,
                'grade_level_id': interest_grade_level_id,
                'school_grade_ids': [(0, 0, {
                    'school_code_id': school_code_id,
                    'grade_level_id': interest_grade_level_id,
                    })],
                "family_ids": [(6, 0, [family_id.id])],
                'date_of_birth': birthday,
                'gender': gender and int(gender) or False,
                'mobile': mobile_1,
                'family_res_finance_ids': family_res_finance,
                'home_address_id': home_address_id.id
            })
            family_id.write({'member_ids': [(4, id_student.id)]})

            # Create an inquiry for each new student
            new_inquiry = InquiryEnv.sudo().create({
                "partner_id": id_student.id,
                'first_name': first_name,
                'middle_name': middle_name,
                'last_name': last_name,
#                 'current_grade_level_id': current_grade_level and int(current_grade_level) or False,
                'grade_level_id': interest_grade_level and int(interest_grade_level) or False,
                'school_year_id': current_school_code and int(current_school_code) or False,
                'responsible_id': [(6,0,parents_ids_created)],
                'sources_id': source_id,
                'source_other': other_source,
                'known_people_in_school': known_people_in_school
            })
            
            id_student.inquiry_id = new_inquiry.id
            id_students.append(id_student)

            if params.get("message"):
                new_inquiry.message_post(body="Message/Question: %s" % params["message"])

        response = http.request.render('adm.template_inquiry_sent')
        return response
