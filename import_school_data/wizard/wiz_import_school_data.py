# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import time
from datetime import datetime
import tempfile
import binascii
from datetime import date, datetime
from odoo.exceptions import Warning, UserError
from odoo import models, fields, exceptions, api, _
import logging

_logger = logging.getLogger(__name__)
import io

try:
    import xlrd
except ImportError:
    _logger.debug('Cannot `import xlrd`.')
try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class ImportChartAccount(models.TransientModel):
    _name = "import.chart.account"

    File_slect = fields.Binary(string="Select Excel File")
    # import_option = fields.Selection([('csv', 'CSV File'),('xls', 'XLS File')],string='Select',default='csv')
    import_option = fields.Selection([('xls', 'XLS File')], string='Select', default='csv')

    def imoport_file(self):

        if self.import_option == 'xls':
            try:
                fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                fp.write(binascii.a2b_base64(self.File_slect))
                fp.seek(0)
                values = {}
                workbook = xlrd.open_workbook(fp.name)
                sheet = workbook.sheet_by_index(0)

            except:
                raise Warning(_("Invalid file!"))

            previous_link_id = -1
            family_id = 0
            home_address_id = 0

            for row_no in range(sheet.nrows):
                val = {}
                if row_no <= 1:
                    fields = map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
                else:

                    line = list(
                        map(lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value),
                            sheet.row(row_no)))
                    # FAMILY DATA
                    link_id = line[0]
                    company_id = line[1]
                    family_name = line[2]
                    # #############

                    # HOME ADDRESS
                    country_id = line[3]
                    state_id = line[4]
                    city = line[5]
                    street = line[6]
                    street2 = line[7]
                    zip = line[8]
                    # #############

                    # PERSON DATA
                    person_type = line[9]
                    first_name = line[10]
                    middle_name = line[11]
                    last_name = line[12]
                    phone = line[13]
                    mobile = line[14]
                    email = line[15]
                    date_of_birth = line[16]
                    gender = line[17]
                    tax_id = line[18]
                    # student data
                    school_code = line[19]
                    school_year = line[20]
                    grade_level = line[21]
                    status = line[22]
                    # #############

                    # RELATIONSHIP DATA
                    relation_type = line[23]
                    custody = line[24]
                    financial_responsability = line[25]
                    family_portal = line[26]
                    grand_parent = line[27]
                    correspondence = line[28]
                    grade_related = line[29]
                    is_an_emergency_contact = line[30]
                    # #############
                    if company_id == '' and family_name == '':
                        pass
                    if previous_link_id == -1 or previous_link_id != link_id:
                        family_id = self.create_family(company_id, family_name, country_id, state_id, city, street,
                                                       street2, zip)
                        home_address_id = self.create_home_address(country_id, state_id, city, street, street2, zip,
                                                                   family_id).id
                    date_aux = False
                    if date_of_birth:
                        date_aux = datetime.strptime(date_of_birth, "%d/%m/%Y").strftime("%Y-%m-%d")
                    person_data = {
                        "person_type": person_type,
                        "first_name": first_name,
                        "middle_name": middle_name,
                        "last_name": last_name,
                        "phone": phone,
                        "mobile": mobile,
                        "email": email,
                        "date_of_birth": date_aux,
                        "home_address_id": home_address_id,
                        "gender": self.env['school_base.gender'].sudo().search([("key", '=', gender)]).id or False,
                        "vat": tax_id,
                        "family_ids": [(4, family_id.id)]
                    }

                    member_id = self.env['res.partner'].sudo().create(person_data)
                    # asociamos los miembros tambien con la familia
                    self.env['res.partner'].sudo().browse(family_id.id).member_ids = [(4, member_id.id)]

                    if str(person_type).lower() == 'student':
                        school_code_id = self.env['school_base.school_code'].sudo().search(
                            [('name', '=', school_code)])
                        grade_level_id = self.env['school_base.grade_level'].sudo().search(
                            [('name', '=', grade_level), ('school_code_id', '=', school_code_id.id)])
                        school_year_id = self.env['school_base.school_year'].sudo().search(
                            [('name', '=', school_year), ('school_code_id', '=', school_code_id.id)])
                        student_status_id = self.env['school_base.enrollment.status'].sudo().search(
                            [('key', '=', status)])
                        self.env['res.partner'].browse(member_id.id).write({
                            "grade_level_id": grade_level_id.id,
                            "student_status_id": student_status_id,
                            "school_code_id": school_code_id,
                            "school_year_id": school_year_id
                        })
                    # es parent
                    else:
                        # actualizo el financial responsability si fuera necesario
                        if True if financial_responsability == '1' else False:
                            self.env['res.partner'].sudo().browse(family_id.id).financial_res_ids = [(4, member_id.id)]

                        stds_ids = self.env['res.partner'].sudo().search(
                            [('person_type', '=', 'student'), ("family_ids", "in", [family_id.id])])
                        _logger.info("STD_IDS")
                        _logger.info(str(stds_ids))
                        for std in stds_ids:
                            _logger.info(str({
                                "relationship_type_id": self.env['school_base.relationship_type'].search(
                                    [('key', '=', relation_type)]).id or False,
                                # "relationship_type_id": 2,
                                "family_id": family_id.id,
                                "partner_individual_id": std.id,
                                "partner_relation_id": member_id.id,
                                "is_emergency_contact": True if is_an_emergency_contact == '1' else False,
                                "custody": True if custody == '1' else False,
                                "correspondence": True if correspondence == '1' else False,
                                "grand_parent": True if grand_parent == '1' else False,
                                "grade_related": True if grade_related == '1' else False,
                                "family_portal": True if family_portal == '1' else False
                            }))
                            self.env['school_base.relationship'].sudo().write({
                                "relationship_type_id": self.env['school_base.relationship_type'].search(
                                    [('key', '=', relation_type)]).id or False,
                                # "relationship_type_id": 2,
                                "family_id": family_id.id,
                                "partner_individual_id": std.id,
                                "partner_relation_id": member_id.id,
                                "is_emergency_contact": True if is_an_emergency_contact == '1' else False,
                                "custody": True if custody == '1' else False,
                                "correspondence": True if correspondence == '1' else False,
                                "grand_parent": True if grand_parent == '1' else False,
                                "grade_related": True if grade_related == '1' else False,
                                "family_portal": True if family_portal == '1' else False
                            })
                    previous_link_id = link_id
        else:
            raise Warning(_("Please select any one from xls or csv formate!"))

        return True

    def create_family(self, company_id, family_name, country_id, state_id, city, street, street2, zip):
        return self.env['res.partner'].sudo().create({
            "is_company": True,
            "is_family": True,
            "company_id": int(company_id),
            "name": family_name,
            "country_id": self.env['res.country'].search([('code', '=', country_id)]).id or False,
            "state_id": self.env['res.country.state'].search([('code', '=', state_id)]).id or False,
            "city": city,
            "street": street,
            "street2": street2,
            "zip": zip
        })

    def create_home_address(self, country_id, state_id, city, street, street2, zip, family_id):
        return self.env['school_base.home_address'].sudo().create({
            "country_id": self.env['res.country'].search([('code', '=', country_id)]).id or False,
            "state_id": self.env['res.country.state'].search([('code', '=', state_id)]).id or False,
            "city": city,
            "street": street,
            "street2": street2,
            "zip": zip,
            "family_id": family_id.id})
