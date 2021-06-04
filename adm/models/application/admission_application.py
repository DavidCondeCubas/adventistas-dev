# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.addons.adm.utils import formatting
from odoo.tools.safe_eval import safe_eval
from ast import literal_eval

import base64
import hashlib
import datetime
import time
from lxml import etree


class Questions(models.Model):
    _name = 'adm.application.question'
    _description = "Application question"

    question = fields.Char(string="Question")
    answer = fields.Char(string="Answer")


class ApplicationStatus(models.Model):
    _name = 'adm.application.status'
    _description = "Application status"
    _order = "sequence"

    name = fields.Char(string="Status Name")
    description = fields.Text(string="Description")
    sequence = fields.Integer(readonly=True, default=-1)

    mail_template_id = fields.Many2one(
        'mail.template', string='Email Template',
        domain=[('model', '=', 'adm.application')],
        help="If set an email will be sent to the customer when "
             "the application reaches this status")

    fold = fields.Boolean(string="Fold")
    type_id = fields.Selection([
        ("stage", "Stage"),
        ("done", "Done"),
        ("return", "Return To Parents"),
        ("started", "Application Started"),
        ("submitted", "Submitted"),
        ("import_completed", "Import Completed"),
        ("cancelled", "Cancelled")
        ], string="Type", default='stage')
    web_visible = fields.Boolean(string="Visible on web")
    web_alternative_name = fields.Char("Alternative name for web")
    hide_if_cancel = fields.Boolean(string="Hide if cancelled")
    hide_if_done = fields.Boolean(string="Hide if done")

    partner_id = fields.Many2one("res.partner", string="Customer")

    task_ids = fields.One2many(
        "adm.application.task", "status_id", "Status Ids")
    new_user_email_template = fields.Many2one(
        "mail.template", string="New user Accepted Admission")
    existed_user_email_template = fields.Many2one(
        "mail.template", string="Existed user Accepted Admission")

    current_year_status_to_facts = fields.Many2one(
        "school_base.enrollment.status", string="Current status to FACTS")
    current_year_next_status_to_facts = fields.Many2one(
        "school_base.enrollment.status", string="Next status to FACTS")

    next_years_status_to_facts = fields.Many2one(
        "school_base.enrollment.status", string="Current status to FACTS")
    next_years_next_status_to_facts = fields.Many2one(
        "school_base.enrollment.status", string="Next status to FACTS")

    import_to_facts = fields.Boolean()

    @api.model
    def create(self, values):
        next_order = self.env['ir.sequence'].next_by_code(
            'sequence.application.task')

        values['sequence'] = next_order
        return super().create(values)


class Gender(models.Model):
    _name = 'adm.gender'
    _description = "Admission Gender"

    name = fields.Char("Gender")


class Application(models.Model):
    ######################
    # Private attributes #
    ######################
    _name = "adm.application"
    _description = "Admission Application"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    # Admission Information
    preferred_degree_program = fields.Many2one(
        "adm.degree_program", string="Preferred Degree Program")

    # Demographic
    name = fields.Char(string="Name", related="partner_id.name")
    first_name = fields.Char(
        string="First Name", related="partner_id.first_name", readonly=False)
    middle_name = fields.Char(
        string="Middle Name", related="partner_id.middle_name", readonly=False)
    last_name = fields.Char(
        string="Last Name", related="partner_id.last_name", readonly=False)
    date_of_birth = fields.Date(
        string="Date of birth", related="partner_id.date_of_birth", readonly=False)
    identification = fields.Char(
        string="Identification", related="partner_id.identification",
        readonly=False)
    birth_country = fields.Many2one(
        "res.country", string="Birth Country",
        related="partner_id.country_id", readonly=False)
    birth_city = fields.Char(
        "Birth City", related="partner_id.city", readonly=False)
    gender = fields.Many2one(
        "adm.gender", string="Gender", related="partner_id.gender", readonly=False)
    status_history_ids = fields.One2many(
        'adm.application.history.status', 'application_id',
        string="Status history")
    last_time_submitted = fields.Datetime(
        compute='_compute_last_time_submitted', store=True)
    family_id = fields.Many2one(
        'res.partner', domain="[('is_family', '=', True)]", required=True)
    implicated_family_ids = fields.Many2many(
        'res.partner', string="Implicated families",
        compute='_compute_implicated_family_ids')

    finish_datetime = fields.Datetime(
        compute='_compute_finish_date', store=True)
    finish_timeline = fields.Float(compute='_compute_finish_date', store=True)

    responsible_user_id = fields.Many2one('res.users', required=True)
    responsible_user_ids = fields.Many2many('res.users', compute="_compute_responsible_users", string="Responsible User")
    user_access_ids = fields.One2many('adm.application.user.access', 'application_id')
    current_user_access_id = fields.Many2one(
        'adm.application.user.access', compute='compute_current_user_access')
    is_current_school_year = fields.Boolean(
        string="Current school year", compute='_compute_defaults_school_year',
        search='_search_current_school_year')
    is_enrollment_school_year = fields.Boolean(
        string="Enrollment school year",
        compute='_compute_defaults_school_year',
        search='_search_enrollment_school_year')

    user_id = fields.Many2one('res.users', string='Assigned to', tracking=True)
    father_name = fields.Char("Father name")
    mother_name = fields.Char("Mother name")

    attachment_ids = fields.One2many(
        'ir.attachment', 'res_id',
        domain=[('res_model', '=', 'adm.application')], string='Attachments')
    how_hear_about_us_id = fields.Many2one('adm.application.option.how.hear.about.us')

    # Contact
    email = fields.Char(string="Email", related="partner_id.email", index=True)
    phone = fields.Char(string="Phone", related="partner_id.mobile")
    home_phone = fields.Char(string="Home phone", related="partner_id.phone")
    other_contacts_ids = fields.One2many(
        "adm.application.other_contacts", "application_id",
        string="Other Contacts")
    citizenship = fields.Many2one("res.country", string="Citizenship")
    language_spoken = fields.Many2one("adm.language", string="Language Spoken")
    image = fields.Binary("Applicant´s Photo", related="partner_id.image_1920")
    # School
    current_school = fields.Char(string="Current School")
    current_school_address = fields.Char(string="Current School Address")

    grade_level_id = fields.Many2one(
        "school_base.grade_level", string="Grade Level",
        domain=[('active_admissions', '=', True)])
    grade_level_type = fields.Selection(
        related="grade_level_id.user_type_id.type")
    grade_level_inquiry = fields.Many2one(
        string="GradeLevel", related="inquiry_id.grade_level_id")
    school_year_id = fields.Many2one(
        "school_base.school_year", string="School Year")
    available_tuition_plan_ids = fields.Many2many(
        'tuition.plan', compute='_compute_available_tuition_plan_ids')
    tuition_plan_id = fields.Many2one('tuition.plan')

    previous_school = fields.Char(string="Previous School")
    previous_school_address = fields.Char(string="Previous School Address")

    gpa = fields.Float("GPA")
    cumulative_grades = fields.Float("Cumulative Grade")
    regional_exam_grade = fields.Float("Regional Grade")
    bac_grade = fields.Float("BAC Grade")

    # Skills
    language_ids = fields.One2many(
        "adm.application.language", "application_id",
        string="Languages", kwargs={"website_form_blacklisted": False})

    primary_language_at_home_id = fields.Many2one('adm.language')

    # Location
    country_id = fields.Many2one(
        "res.country", related="partner_id.country_id", string="Country")
    state_id = fields.Many2one(
        "res.country.state", related="partner_id.state_id", string="State")
    city = fields.Char(string="City", related="partner_id.city")
    street = fields.Char(string="Street Address", related="partner_id.street")
    zip = fields.Char("zip", related="partner_id.zip")

    # Relationships
    student_relationship_ids = fields.Many2many(
        'school_base.relationship', string="Relationship",
        related="partner_id.self_relationship_ids", readonly=False)

    parent_relationship_ids = fields.One2many(
        'school_base.relationship',
        string="Parents/Guardian",
        # compute="compute_relationships",
        # inverse="_set_parent_relationships",
        related='partner_id.parent_relationship_ids',
        readonly=False,
        )

    sibling_relationship_ids = fields.One2many(
        'school_base.relationship',
        string="Siblings",
        # compute="compute_relationships",
        # inverse="_set_sibling_relationships",
        related='partner_id.sibling_relationship_ids',
        readonly=False,
        store=False
        )

    other_relationship_ids = fields.One2many(
        'school_base.relationship',
        string="Others",
        # compute="compute_relationships",
        # inverse="_set_other_relationships",
        related='partner_id.other_relationship_ids',
        readonly=False,
        store=False
        )

    custodial_relationship_ids = fields.Many2many(
        'school_base.relationship', string="Custody contacts",
        related='partner_id.custodial_relationship_ids', store=False)
    # Documentation
    letter_of_motivation_id = fields.Many2one(
        "ir.attachment", string="Letter of motivation")
    cv_id = fields.Many2one("ir.attachment", string="C.V")
    grade_transcript_id = fields.Many2one(
        "ir.attachment", string="Grade transcript")
    letters_of_recommendation_id = fields.Many2one(
        "ir.attachment", string="Letter of recommendation")

    # Additional student info
    resident_status = fields.Selection(
        [('permanent', 'Permanent'), ('transient', 'Transient'), ],
        string="Resident status")
    resident_length_of_stay = fields.Char("Length of stay")

    # languages level
    languages_levels = [
        ("beginner", "Beginner"), ("elementary", "Elementary"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"), ("fluent", "Fluent")
        ]
    first_level_language = fields.Selection(
        languages_levels, string="Level", default='beginner')
    second_level_language = fields.Selection(
        languages_levels, string="Level", default='beginner')
    third_level_language = fields.Selection(
        languages_levels, string="Level", default='beginner')

    number_years_in_english = fields.Char("Years in English")
    additional_info_other = fields.Char("Other")

    special_education = fields.Boolean("Special Education")
    special_education_desc = fields.Text("Special Education Description")

    psycho_educational_testing = fields.Boolean("Psycho educational testing")

    emotional_support = fields.Boolean("Emotional support")
    emotional_support_desc = fields.Text("Emotional support description")

    iep_education = fields.Boolean("IEP Education")

    # Previous School
    previous_school_ids = fields.One2many("adm.previous.school.description", "application_id")

    # References
    isp_community_reference_1 = fields.Char("ISP Community Reference #1")
    isp_community_reference_2 = fields.Char("ISP Community Reference #2")

    personal_reference_contact_information_1 = fields.Char(
        "Personal Reference #1 Contact Information:")
    personal_reference_name_1 = fields.Char("Personal Reference #1 Name")

    personal_reference_contact_information_2 = fields.Char(
        "Personal Reference #2 Contact Information:")
    personal_reference_name_2 = fields.Char("Personal Reference #2 Name")

    # Medical information
    doctor_name = fields.Char(
        "Doctor name", related='partner_id.doctor_name', readonly=False)
    doctor_phone = fields.Char(
        "Doctor phone", related='partner_id.doctor_phone', readonly=False)
    doctor_address = fields.Char(
        "Doctor Direction", related='partner_id.doctor_address',
        readonly=False)
    hospital = fields.Char(
        "Hospital", related='partner_id.hospital', readonly=False)
    hospital_address = fields.Char(
        "Hospital Address", related='partner_id.hospital_address',
        readonly=False)
    permission_to_treat = fields.Boolean(
        "Permission To Treat", related='partner_id.permission_to_treat',
        readonly=False)
    blood_type = fields.Char(
        "Blood Type", related='partner_id.blood_type', readonly=False)

    medical_allergies_ids = fields.One2many(
        string="Allergies", related="partner_id.medical_allergies_ids",
        readonly=False)
    medical_conditions_ids = fields.One2many(
        string="Conditions", related="partner_id.medical_conditions_ids",
        readonly=False)
    medical_medications_ids = fields.One2many(
        string="Medications", related="partner_id.medical_medications_ids",
        readonly=False)

    # Meta
    contact_time_id = fields.Many2one(
        "adm.contact_time", string="Preferred contact time")

    partner_id = fields.Many2one("res.partner", string="Contact")
    partner_family_ids = fields.Many2many('res.partner', related='partner_id.family_ids')
    partner_family_member_ids = fields.Many2many('res.partner', related='partner_id.family_member_ids')

    status_id = fields.Many2one(
        "adm.application.status", string="Status",
        group_expand="_read_group_status_ids")
    task_ids = fields.Many2many("adm.application.task")

    are_stage_task_complete = fields.Boolean(
        "Are all task complete", compute='compute_all_task_complete',
        store=True)

    inquiry_id = fields.Many2one("adm.inquiry")

    state_tasks = fields.One2many(
        string="State task", related="status_id.task_ids")

    status_type = fields.Selection(
        string="Status Type", related="status_id.type_id")
    forcing = False

    # QUESTION CUSTOMIZED PREESCOLAR
    applying_semester = fields.Selection(
        [
            ('semester_1', 'Semester 1 (August)'),
            ('semester_2', 'Semester 2 (January)'),
            ('immediate', 'Immediate'),
            ], string="Applying semester")

    # Files
    birth_certificate_attachment_ids = fields.Many2many(
        'ir.attachment', relation='application_birth_certificates')
    immunization_records_attachment_ids = fields.Many2many(
        'ir.attachment', relation='application_immunization_records')
    custody_documents_attachment_ids = fields.Many2many(
        'ir.attachment', relation='application_custody_documents')
    current_report_card_attachment_ids = fields.Many2many(
        'ir.attachment', relation='application_current_report_cards')
    standardized_test_attachment_ids = fields.Many2many(
        'ir.attachment', relation='application_standardized_tests')

    passport_file_ids = fields.Many2many(
        'ir.attachment', 'application_passport_id')
    residency_file_ids = fields.Many2many(
        'ir.attachment', 'application_residency_id')

    residency_permit_id_number = fields.Many2one('ir.attachment')
    parent_passport_upload = fields.Many2one('ir.attachment')

    # Fields compute percentage
    required_fields_completed = fields.Integer(
        string="Required fields completed",
        compute="_compute_application_fields")
    optional_fields_completed = fields.Integer(
        string="Optional fields completed",
        compute="_compute_application_fields")
    fields_completed = fields.Float(
        string="Fields completed", compute="_compute_application_fields")

    total_required_fields_completed = fields.Float(
        string="Total required fields completed",
        compute="_compute_application_fields")
    total_optional_fields_completed = fields.Float(
        string="Total optional fields completed",
        compute="_compute_application_fields")
    total_fields_completed = fields.Float(
        string="Total fields completed", compute="_compute_application_fields")

    # Signature
    signature_attach_url = fields.Char("Signature Attachment URL")
    signature_person_name = fields.Char()
    signature_agreements = fields.Boolean(string="Signature agreements")
    check_confidential_info_adm_file = fields.Boolean(
        string="Rights to access confidential information "
               "contained in applicant's admission file.")

    signature_date = fields.Date()

    ##############################
    # Compute and search methods #
    ##############################
    @api.depends("first_name", "middle_name", "last_name")
    def _update_contact(self):
        for record in self:
            record.partner_id.first_name = record.first_name

    def _compute_implicated_family_ids(self):
        for application_id in self:
            application_id.implicated_family_ids = False

    def _compute_responsible_users(self):
        for application_id in self:
            application_id.responsible_user_ids = application_id.mapped('user_access_ids.user_id')

    def _compute_defaults_school_year(self):
        for application_id in self:
            current_school_year = self.env.company.current_school_year_id
            enrollment_school_year = self.env.company.enrollment_school_year_id

            application_id.is_current_school_year = (
                    application_id.school_year_id
                    or current_school_year
                    or application_id.school_year_id == current_school_year)
            application_id.is_enrollment_school_year = (
                    application_id.school_year_id
                    or current_school_year
                    or application_id.school_year_id == enrollment_school_year)

    def compute_current_user_access(self):
        for application in self:
            user_access = application.user_access_ids.filtered(
                lambda us: us.user_id == self.env.user
                ).sorted('create_date', reverse=True)
            application.current_user_access_id = user_access[:1]

    @api.depends('status_history_ids')
    def _compute_last_time_submitted(self):
        for application_id in self:
            submitted_status = application_id.status_history_ids.filtered(
                lambda sh: sh.status_id.type_id == 'submitted')[:1]
            application_id.last_time_submitted = submitted_status.timestamp

    @api.depends('status_id', 'status_id.type_id')
    def _compute_finish_date(self):
        for application_id in self:
            if application_id.status_id.type_id == 'done':
                now = datetime.datetime.now()
                application_id.finish_datetime = now
                application_id.finish_timeline = 0

    @api.model
    def _create_relation_if_not_exists(self, relationships):
        rels = relationships.filtered(lambda r: r._origin)
        for relation in relationships:
            if not relation._origin:
                rels += relation.copy()
        return rels

    def _set_parent_relationships(self):
        for application_id in self:
            application_id.partner_id.parent_relationship_ids = application_id.parent_relationship_ids

    def _set_sibling_relationships(self):
        for application_id in self:
            application_id.partner_id.sibling_relationship_ids = application_id.sibling_relationship_ids

    def _set_other_relationships(self):
        for application_id in self:
            application_id.partner_id.other_relationship_ids = application_id.other_relationship_ids

    def _compute_application_fields(self):
        for application_id in self:
            required_field_ids = self.get_required_fields()
            application_id.required_fields_completed = sum(
                required_field_ids.mapped(
                    lambda f: not not application_id[f.name]))
            if required_field_ids:
                application_id.total_required_fields_completed = (
                        application_id.required_fields_completed
                        * 100
                        / len(required_field_ids))
            else:
                application_id.total_required_fields_completed = 0

            optional_field_ids = self.get_optional_fields()
            application_id.optional_fields_completed = sum(
                optional_field_ids.mapped(
                    lambda f: not not application_id[f.name]))
            if optional_field_ids:
                application_id.total_optional_fields_completed = (
                        application_id.optional_fields_completed
                        * 100
                        / len(optional_field_ids))
            else:
                application_id.total_optional_fields_completed = 0

            # Required fields first
            application_id.fields_completed = (
                    application_id.required_fields_completed
                    + application_id.optional_fields_completed)
            if required_field_ids and optional_field_ids:
                application_id.total_fields_completed = (
                        (application_id.fields_completed * 100)
                        / (len(required_field_ids) + len(optional_field_ids)))
            else:
                application_id.total_fields_completed = 0

    @api.depends('status_id', 'state_tasks', 'task_ids')
    def compute_all_task_complete(self):
        for application_id in self:
            stage_task_completed = (application_id.state_tasks
                                    & application_id.task_ids)
            are_task_completed = \
                stage_task_completed == application_id.state_tasks
            application_id.are_stage_task_complete = are_task_completed

    @api.depends("first_name", "middle_name", "last_name")
    def _compute_name(self):
        for record in self:
            record.name = formatting.format_name(
                record.first_name, record.middle_name, record.last_name)
            record.partner_id.first_name = record.first_name

    def _set_family_id(self):
        for application_id in self:
            application_id.family_id = application_id.family_id

    def _search_current_school_year(self, operator, value):
        current_school_year = self.env.company.current_school_year_id

        if value:
            operator = '='
        else:
            operator = '!='

        return [('school_year_id', operator, current_school_year.id)]

    def _search_enrollment_school_year(self, operator, value):
        enrollment_school_year = self.env.company.enrollment_school_year_id

        if value:
            operator = '='
        else:
            operator = '!='

        return [('school_year_id', operator, enrollment_school_year.id)]

    def _compute_available_tuition_plan_ids(self):
        for application_id in self:
            school_year_id = application_id.school_year_id
            tuition_plan_ids = \
                self.env['tuition.plan'].search([
                    ('period_date_from', '>=', school_year_id.date_start),
                    ('period_date_from', '<=', school_year_id.date_end),
                    ('grade_level_ids', '=', application_id.grade_level_id.id)
                    ])
            application_id.available_tuition_plan_ids = tuition_plan_ids

    ############################
    # Constrains and onchanges #
    ############################
    @api.onchange("country_id")
    def _onchange_country_id(self):
        res = {}
        if self.country_id:
            res['domain'] = {
                'state_id': [('country_id', '=', self.country_id.id)]
                }

    @api.onchange("first_name", "middle_name", "last_name")
    def _set_full_name(self):
        self.name = formatting.format_name(
            self.first_name, self.middle_name, self.last_name)

    #########################
    # CRUD method overrides #
    #########################
    @api.model
    def _read_group_status_ids(self, stages, domain, order):
        status_ids = self.env['adm.application.status'].search([])
        return status_ids

    @api.model
    def create(self, values):
        if not values.get('status_id', False):
            status_id = self.env['adm.application.status'].search(
                [], order="sequence")[0]
            values['status_id'] = status_id.id
        else:
            status_id = self.env['adm.application.status'].browse(
                values['status_id'])
        # values['name'] = formatting.format_name(values['first_name'],
        # values['middle_name'], values['last_name'])
        application_id = super(Application, self).create(values)

        member_ids = application_id.partner_id.mapped('family_ids.member_ids')

        application_id.message_subscribe(
            partner_ids=member_ids.filtered(
                lambda m: m.person_type == 'parent').ids)

        message = _("Application created in [%s] status") % status_id.name
        timestamp = datetime.datetime.now()

        self.env['adm.application.history.status'].sudo().create({
            'note': message,
            'timestamp': timestamp,
            'application_id': application_id.id,
            'status_id': status_id.id,
            })

        if status_id.mail_template_id:
            application_id.message_post_with_template(
                template_id=status_id.mail_template_id.id,
                res_id=application_id.id)

        return application_id

    def write(self, values):
        for application_id in self:
            first_name = values.get('first_name', application_id.first_name)
            middle_name = values.get('middle_name', application_id.middle_name)
            last_name = values.get('last_name', application_id.last_name)

            # "related" in application_id.fields_get()["email"]
            # Se puede hacer totalmente dinamico, no lo hago ahora por falta de
            # tiempo
            # Pero sin embargo, es totalmente posible.
            # Los no related directamente no tiene related, y los que si son
            # tiene el campo related de la siguiente manera: (model, field)
            # fields = application_id.fields_get()
            partner_related_fields = {}
            partner_fields = [
                'email', 'phone', 'home_phone', 'country_id', 'state_id',
                'city', 'street', 'zip', 'date_of_birth', 'identification'
                ]
            for partner_field in partner_fields:
                if partner_field in values:
                    partner_related_fields[partner_field] = \
                        values[partner_field]

            if "first_name" in values:
                partner_related_fields["first_name"] = first_name
            if "middle_name" in values:
                partner_related_fields["middle_name"] = middle_name
            if "last_name" in values:
                partner_related_fields["last_name"] = last_name

            application_id.sudo().partner_id.write(partner_related_fields)

            # PARA PONER VALOR POR DEFECTO
            # application_id._context.get('forcing', False):

            if values.get('status_id', False):
                next_status_id = \
                    application_id.env['adm.application.status'].browse(
                        values['status_id'])

                message = _("From [%s] to [%s] status") % (
                    application_id.status_id.name, next_status_id.name)
                timestamp = datetime.datetime.now()

                self.env['adm.application.history.status'].sudo().create({
                    'note': message,
                    'timestamp': timestamp,
                    'application_id': application_id.id,
                    'status_id': next_status_id.id,
                    })

                if next_status_id.mail_template_id:
                    application_id.message_post_with_template(
                        template_id=next_status_id.mail_template_id.id,
                        res_id=application_id.id)

                if not self._context.get('forcing', False):
                    if not application_id.are_stage_task_complete:
                        raise exceptions.ValidationError(
                            _("All task are not completed"))
            else:
                application_id.forcing = False

            member_ids = application_id.partner_id.mapped(
                'family_ids.member_ids')

            application_id.message_subscribe(
                partner_ids=member_ids.filtered(
                    lambda m: m.person_type == 'parent').ids)

        return super(Application, self).write(values)

    ##################
    # Action methods #
    ##################
    def cancel(self):

        status_ids_ordered = self.env['adm.application.status'].search(
            [], order="sequence")

        for status in status_ids_ordered:
            if status.type_id == 'cancelled':
                self.status_id = status
                break

    def print_default(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/report/html/adm.report_default/' + str(self.id),
            'target': '_blank',
            'res_id': self.id,
            }

    def print_custom(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/report/html/adm.report_custom/' + str(self.id),
            'target': '_blank',
            'res_id': self.id,
            }

    def force_back(self):
        status_ids_ordered = self.env['adm.application.status'].search(
            [], order="sequence")
        index = 0
        for status in status_ids_ordered:
            if status == self.status_id:
                break
            index += 1

        index -= 1
        if index >= 0:
            next_status = status_ids_ordered[index]
            self.with_context({
                'forcing': True
                }).status_id = next_status

    def force_next(self):
        status_ids_ordered = self.env['adm.application.status'].sudo().search(
            [], order="sequence")
        index = 0
        for status in status_ids_ordered:
            if status == self.status_id:
                break
            index += 1

        index += 1
        if index < len(status_ids_ordered):
            next_status = status_ids_ordered[index]
            self.with_context({
                'forcing': True
                }).status_id = next_status

    def generate_internal_report(self):
        """  Generate the internal report and will save int
             attachment of the application """
        AttachmentEnv = self.env["ir.attachment"]
        REPORT_ID = 'adm.report_internal_custom'
        pdf = self.env.ref(REPORT_ID).render_qweb_pdf(self.ids)
        # pdf result is a list
        b64_pdf = base64.b64encode(pdf[0])
        # save pdf as attachment
        # requests.session = request.session

        file_id = AttachmentEnv.sudo().create({
            'name': 'Internal Report',  # 'datas_fname': upload_file.filename,
            'res_name': 'reportInternal.pdf',
            'type': 'binary',
            'res_model': 'adm.application',
            'res_id': self.id,
            'datas': b64_pdf,
            })

        return {
            'type': 'ir.actions.act_url',
            'url': '/report/html/adm.report_custom/' + str(self.id),
            'target': '_blank',
            'res_id': self.id,
            }

    ####################
    # Business methods #
    ####################
    def get_required_fields(self):
        # First we get the all the fields
        config_parameter = self.env['ir.config_parameter'].sudo()
        application_required_fields_str = config_parameter.get_param(
            'adm_application_required_field_ids', '')
        application_required_fields = [
            int(e)
            for e in application_required_fields_str.split(',')
            if e.isdigit()
            ]
        required_field_ids = self.env['adm.fields.settings'].sudo().browse(
            application_required_fields)

        # Then we filter by the field domain
        filtered_required_fields_ids = self.env['adm.fields.settings'].sudo()
        for required_field_id in required_field_ids:
            field_domain = safe_eval(required_field_id.domain or '[]')
            if self.filtered_domain(field_domain):
                filtered_required_fields_ids += required_field_id

        return filtered_required_fields_ids

    def get_optional_fields(self):
        application_optional_fields_str = \
            self.env['ir.config_parameter'].sudo().get_param(
                'adm_application_optional_field_ids', '')
        application_optional_fields = [
            int(e)
            for e in application_optional_fields_str.split(',')
            if e.isdigit()
            ]
        optional_field_ids = self.env['adm.fields.settings'].sudo().browse(
            application_optional_fields)

        filtered_optional_field_ids = self.env['adm.fields.settings'].sudo()
        for required_field_id in optional_field_ids:
            field_domain = safe_eval(required_field_id.domain or '[]')
            if self.filtered_domain(field_domain):
                filtered_optional_field_ids += optional_field_ids

        return filtered_optional_field_ids

    def message_get_suggested_recipients(self):
        recipients = super().message_get_suggested_recipients()
        try:
            for inquiry in self:
                if inquiry.email:
                    inquiry._message_add_suggested_recipient(
                        recipients, partner=self.partner_id,
                        email=inquiry.email, reason=_('Custom Email Luis'))
        except exceptions.AccessError:
            # no read access rights -> just ignore
            # suggested recipients because this imply modifying followers
            pass
        return recipients

    def force_status_submitted(self, next_status_id):
        self.with_context({
            'forcing': True
            }).status_id = next_status_id

    def move_to_next_status(self):
        self.forcing = False
        status_ids_ordered = self.env['adm.application.status'].search([], order="sequence")
        index = 0
        for status in status_ids_ordered:
            if status == self.status_id:
                # print("Encontrado! -> {}".format(index))
                break
            index += 1

        index += 1
        if index < len(status_ids_ordered):
            next_status = status_ids_ordered[index]

            if self.status_id.type_id == 'done':
                raise exceptions.except_orm(
                    _('Application completed'),
                    _('The Application is already done'))
            elif self.status_id.type_id == 'cancelled':
                raise exceptions.except_orm(
                    _('Application cancelled'),
                    _('The Application cancelled'))
            else:
                self.status_id = next_status

    def get_partner_invitation(self, email, access=False, mail_template=False):
        self.ensure_one()
        if not access:
            access = []

        if not mail_template:
            mail_template = \
                self.env.company.sudo().mail_inviting_partner_to_application_id

        invitation = self.env['adm.application.invitation'].sudo().create({
            'application_id': self.id,
            'by_partner_id': self.env.user.partner_id.id,
            'to_email': email,
            'mail_template_id': mail_template.id,
            # 'access_ids': [(6, 0, access)]
            })

        return invitation

    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        View = self.env['ir.ui.view']

        if view_type == 'form':
            doc = etree.XML(res['arch'])
            res_fields = res.get('fields', {})
            for node in doc.xpath('//page[@name="custom_page"]/notebook'):
                pages = self.env['adm.application.fields.configuration'].search([])
                for page in pages:
                    xml_page = etree.Element('page', string=page.name)
                    xml_group = etree.SubElement(xml_page, 'group')
                    for field_config in page.field_ids:
                        field_id = field_config.field_id
                        context = field_config.custom_context
                        attrs = field_config.custom_attrs
                        field_el = etree.SubElement(xml_group, 'field',
                                                    name=field_id.name,
                                                    attrs=attrs,
                                                    context=context,)
                        self.fields_get()
                        if field_config.custom_xml_to_render:
                            xml_to_render_el = etree.fromstring(field_config.custom_xml_to_render)
                            field_el.append(xml_to_render_el)

                    xarch, xfields = View.postprocess_and_fields(self._name, xml_page, view_id)
                    node.append(etree.XML(xarch))
                    res_fields.update(xfields)
            res['arch'] = etree.tostring(doc, encoding='unicode', method='xml')
            res['fields'] = res_fields

        return res

    ####################
    # Private methods #
    ####################
    def _message_get_default_recipients(self):
        res = {}
        for application in self:
            recipient_ids, email_to, email_cc = [], False, False
            partner_follower_ids = application.mapped('message_follower_ids.partner_id')
            recipient_ids.extend(partner_follower_ids.ids)
            # email_to =
            # if 'partner_id' in record and record.partner_id:
            #     recipient_ids.append(record.partner_id.id)
            # elif 'email_normalized' in record and record.email_normalized:
            #     email_to = record.email_normalized
            # elif 'email_from' in record and record.email_from:
            #     email_to = record.email_from
            # elif 'partner_email' in record and record.partner_email:
            #     email_to = record.partner_email
            # elif 'email' in record and record.email:
            #     email_to = record.email
            res[application.id] = {
                'partner_ids': recipient_ids,
                'email_to': email_to,
                'email_cc': email_cc
                }
        return res


class AdmApplicationInvitation(models.Model):
    ######################
    # Private attributes #
    ######################
    _name = 'adm.application.invitation'
    _description = "Application invitation"

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    salt = fields.Char('Salt', readonly=True, required=True)
    secure_hash = fields.Char(readonly=True, required=True)
    by_partner_id = fields.Many2one(
        'res.partner', string='Invited by', required=True)
    to_email = fields.Char('To email', required=True)

    mail_template_id = fields.Many2one('mail.template')

    mail_id = fields.Many2one('mail.message')
    mail_body = fields.Html(related='mail_id.body')
    application_id = fields.Many2one('adm.application', required=True)
    invited_user_id = fields.Many2one('res.users')
    access_family_id = fields.Many2one('res.partner', domain="[('is_family', '=', True)]")

    state = fields.Selection([
        ('accepted', _("Accepted")),
        ('rejected', _("Rejected")),
        ])
    page_access_ids = fields.Many2many('adm.application.page')

    url = fields.Char(compute='compute_url')

    def compute_url(self):
        for invitation_id in self:
            invitation_id.url = (
                "/admission/application/%i/invite/%i/%s"
                % (invitation_id.application_id.id, invitation_id.id, invitation_id.secure_hash))

    @api.model
    def create(self, vals):

        salt = hashlib.sha256(str(time.time()).encode('utf-8')).hexdigest()
        to_email = vals['to_email']
        application_id = vals.get('application_id', 0)

        text_to_hash = '%s%i-%s' % (salt, application_id, to_email)
        secure_hash = hashlib.sha256(text_to_hash.encode('utf-8')).hexdigest()

        vals['salt'] = salt
        vals['secure_hash'] = secure_hash

        invited_user = self.env['res.users'].search([('partner_id.email', '=', to_email)])
        vals['invited_user_id'] = invited_user.id

        return super(AdmApplicationInvitation, self).create(vals)

    def write(self, vals):
        super(AdmApplicationInvitation, self).write(vals)
        for invitation in self:
            if (invitation.state == 'accepted'
                    and invitation.access_family_id):

                invitation.application_id.partner_id.write({
                    'family_ids': [(4, invitation.access_family_id.id, False)]
                    })
                invitation.access_family_id.write({
                    'member_ids': [
                        (4, invitation.application_id.partner_id.id, False)
                        ]
                    })


class AdmApplicationUserAccess(models.Model):
    ######################
    # Private attributes #
    ######################
    _name = 'adm.application.user.access'
    _description = "Application user access"

    ######################
    # Fields declaration #
    ######################
    page_access_ids = fields.Many2many('adm.application.page')
    application_id = fields.Many2one('adm.application', required=True)
    user_id = fields.Many2one('res.users', required=True)
    family_id = fields.Many2one('res.partner', required=True)


class AdmApplicationPage(models.Model):
    _name = 'adm.application.page'
    _description = "Application page"
    _order = "sequence"

    active = fields.Boolean(default=True)
    sequence = fields.Integer(default='-1')
    name = fields.Char(translate=True)
    url = fields.Char()
    internal_reference = fields.Char()
    website_id = fields.Many2one('website')
    previous_page_id = fields.Many2one('adm.application.page')
    next_page_id = fields.Many2one('adm.application.page')
    view_template_id = fields.Many2one('ir.ui.view')
    parent_id = fields.Many2one('adm.application.page')
    child_ids = fields.One2many('adm.application.page', 'parent_id')

    _sql_constraints = [
        ('adm_page_internal_reference',
         'unique (internal_reference, website_id)',
         "The internal reference should be unique by website"),
        ]

    @api.model
    def find_by_reference(self, reference):
        return self.search([('internal_reference', '=', reference)])[:1]


class ApplicationOtherContacts(models.Model):
    _name = 'adm.application.other_contacts'
    _description = "Application other contacts"

    contact_name = fields.Char("Contact Name")
    contact_identification = fields.Char("Contact Identification")

    application_id = fields.Many2one("adm.application", string="Application")


class ApplicationTasks(models.Model):
    _name = 'adm.application.task'
    _description = "Application Task"

    name = fields.Char("Name")
    description = fields.Char("Description")
    status_id = fields.Many2one("adm.application.status", string="Status")


class AdmissionApplicationLanguages(models.Model):
    _name = 'adm.application.language'
    _description = "Application language"

    language_id = fields.Many2one("adm.language", string="Language")
    language_level_id = fields.Many2one(
        "adm.language.level", string="Language Level")
    application_id = fields.Many2one("adm.application", string="Application")


class AdmApplicationFieldsConfiguration(models.Model):
    _name = 'adm.application.fields.configuration'
    _description = "Application fields configuration"
    _order = 'sequence'

    name = fields.Char(translate=True, required=True)
    sequence = fields.Integer()

    field_ids = fields.One2many(
        'adm.application.fields.configuration.field',
        'configuration_id',
        string="Fields")


class AdmApplicationFieldsConfigurationField(models.Model):
    _name = 'adm.application.fields.configuration.field'
    _description = "Application fields configuration.field"
    _order = 'sequence'

    def _get_application_model(self):
        return self.env['ir.model'].search([('model', '=', 'adm.application')])

    configuration_id = fields.Many2one('adm.application.fields.configuration')
    sequence = fields.Integer()
    field_id = fields.Many2one('ir.model.fields',
                                 string="Field",
                                 domain="[('model', '=', 'adm.application'), ('state', '=', 'manual')]")
    adm_application_model_id = fields.Many2one('ir.model',
                                               default=_get_application_model,
                                               compute='_compute_application_model')

    custom_xml_to_render = fields.Text("Custom xml to render", help="""
        Used to XML render a custom xml.
        """)
    custom_context = fields.Char(required=True, default='{}')
    custom_attrs = fields.Char(required=True, default='{}')

    def _compute_application_model(self):
        for record in self:
            record.adm_application_model_id = self._get_application_model()
