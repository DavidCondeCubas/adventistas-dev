# -*- encoding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

from ..utils.commons import switch_statement

SELECT_PERSON_TYPES = [
    ("student", "Student"),
    ("parent", "Parent")
    ]

SELECT_COMPANY_TYPES = [
    ("person", "Person"),
    ("company", "Company/Family")
    ]

SELECT_STATUS_TYPES = [
    ("admissions", "Admissions"),
    ("enrolled", "Enrolled"),
    ("graduate", "Graduate"),
    ("inactive", "Inactive"),
    ("pre-enrolled", "Pre-Enrolled"),
    ("withdrawn", "Withdrawn"),
    ]

SELECT_REENROLLMENT_STATUS = [
    ("open", "Open"),
    ("finished", "Finished"),
    ("withdrawn", "Withdrawn"),
    ("rejected", "Rejected"),
    ("blocked", "Blocked"),
]


class ResPartner(models.Model):
    """ We inherit to enable School features for contacts """

    ######################
    # Private Attributes #
    ######################
    _inherit = "res.partner"

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################

    # - Demographics
    name = fields.Char(
        index=True, compute="_compute_name", store=True, readonly=False)

    # Name should be readonly
    allow_edit_student_name = fields.Boolean(
        compute="_retrieve_allow_name_edit_from_config")
    allow_edit_parent_name = fields.Boolean(
        compute="_retrieve_allow_name_edit_from_config")
    allow_edit_person_name = fields.Boolean(
        compute="_retrieve_allow_name_edit_from_config")

    is_name_edit_allowed = fields.Boolean(
        compute="_compute_allow_name_edition")

    first_name = fields.Char("First Name")
    middle_name = fields.Char("Middle Name")
    last_name = fields.Char("Last Name")
    date_of_birth = fields.Date(string='Date of birth')
    suffix = fields.Char("Suffix")
    facts_nickname = fields.Char("Facts Nickname")
    ethnicity = fields.Char("Ethnicity")
    facts_citizenship = fields.Char("Facts Citizenship")
    primary_language = fields.Char("Primary Language")
    birth_city = fields.Char("Birth City")
    birth_state = fields.Char("Birth State")
    birh_place = fields.Char("Birth place")
    race = fields.Char("Race")
    gender = fields.Many2one("school_base.gender", string="Gender")

    ssn = fields.Char()

    id_documentation_file = fields.Binary(attachment=True)
    id_documentation_file_name = fields.Char()

    passport_id = fields.Char('Passport ID')
    passport_expiration_date = fields.Date('Passport expiration date')

    passport_id_file = fields.Binary(attachment=True)
    passport_id_file_name = fields.Char()

    residency_permit_id_file = fields.Binary(attachment=True)
    residency_permit_id_file_name = fields.Char()

    citizenship = fields.Many2one("res.country", string="Citizenship")
    identification = fields.Char("ID number")
    salutation = fields.Char("Salutation")

    marital_status_id = fields.Many2one(
        'school_base.marital_status', string='Marital status')

    occupation = fields.Char("Occupation")
    title = fields.Char("Title")

    # It is known that Odoo has parent_id.
    # But sometime the school just doesn't really care about it and
    # parent_id changes the partner behaviour. So this is more a metadata
    employer = fields.Char("Employer")

    # - Medical
    medical_allergies_ids = fields.One2many(
        "school_base.medical_allergy", "partner_id",
        string="Medical Allergies")
    medical_conditions_ids = fields.One2many(
        "school_base.medical_condition", "partner_id",
        string="Medical conditions")
    medical_medications_ids = fields.One2many(
        "school_base.medical_medication", "partner_id",
        string="Medical Medication")

    allergy_ids = fields.One2many(
        "school_base.allergy", "partner_id", string="Allergies")
    condition_ids = fields.One2many(
        "school_base.condition", "partner_id", string="Conditions")

    doctor_name = fields.Char("Doctor name")
    doctor_phone = fields.Char("Doctor phone")
    doctor_address = fields.Char("Doctor Direction")
    hospital = fields.Char("Hospital")
    hospital_address = fields.Char("Hospital Address")
    permission_to_treat = fields.Boolean("Permission To Treat")
    blood_type = fields.Char("Blood Type")

    # - Conctact
    # This fields are mainly used for the onchange method below
    home_address_name = fields.Char(realated='home_address_id.name')
    home_address_country_id = fields.Many2one(
        realated='home_address_id.country_id')
    home_address_state_id = fields.Many2one(
        realated='home_address_id.state_id')

    home_address_city = fields.Char(realated='home_address_id.city')
    home_address_zip = fields.Char(realated='home_address_id.zip')
    home_address_street = fields.Char(realated='home_address_id.street')
    home_address_street2 = fields.Char(realated='home_address_id.street2')
    home_address_phone = fields.Char(realated='home_address_id.phone')

    # - Academic
    # Fields for current student status, grade leve, status, etc...
    school_code_ids = fields.Many2many('school_base.school_code')
    school_grade_ids = fields.One2many(
        'school_base.partner_school_grade', 'partner_id')
    grade_level_ids = fields.Many2many(
        'school_base.grade_level', compute='compute_grade_levels',
        store=True)

    school_code_id = fields.Many2one(
        'school_base.school_code', string='Current school code')
    grade_level_id = fields.Many2one(
        "school_base.grade_level", string="Grade Level")

    school_year_id = fields.Many2one(
        'school_base.school_year', string="School year",
        help="The school year where the student is enrolled")

    student_status = fields.Char(
        "Student status (Deprecated)", help="(This field is deprecated)")

    student_status_id = fields.Many2one(
        "school_base.enrollment.status", string="Student status")

    # Fields for next student status, grade leve, status, etc...
    next_school_code_id = fields.Many2one(
        'school_base.school_code', string='Next school code')
    next_grade_level_id = fields.Many2one(
        "school_base.grade_level", string="Next grade level")
    student_next_status_id = fields.Many2one(
        "school_base.enrollment.status", string="Student next status")

    home_address_ids = fields.One2many(
        "school_base.home_address", 'family_id', string="Home Addresses", )
    family_home_address_ids = fields.One2many(
        related='family_ids.home_address_ids',
        string="Family Home Addresses", )
    home_address_id = fields.Many2one(
        "school_base.home_address", string="Home Address")

    # - Family Structure
    family_ids = fields.Many2many(
        "res.partner", string="Families",
        relation="partner_families",
        column1="partner_id",
        column2="partner_family_id")
    member_ids = fields.Many2many(
        "res.partner", string="Members",
        relation="partner_members",
        column1="partner_id",
        column2="partner_member_id")
    is_family = fields.Boolean("Is a family?")
    family_member_ids = fields.Many2many(related='family_ids.member_ids')

    member_relationship_ids = fields.One2many(
        'school_base.relationship', 'family_id',
        domain="[('partner_relation_id.active', '=', True), "
               "('partner_individual_id.active', '=', True)]",
        string="Relationships Members")

    self_relationship_ids = fields.Many2many(
        'school_base.relationship', compute='compute_self_relationship_ids')

    parent_relationship_ids = fields.One2many(
        'school_base.relationship', string="Parents/Guardian",
        compute="compute_self_relationship_ids",
        inverse="_set_parent_relationships", readonly=False)

    sibling_relationship_ids = fields.One2many(
        'school_base.relationship', string="Siblings",
        compute="compute_self_relationship_ids",
        inverse="_set_sibling_relationships", readonly=False, store=False)

    other_relationship_ids = fields.One2many(
        'school_base.relationship', string="Others",
        compute="compute_self_relationship_ids",
        inverse="_set_other_relationships", readonly=False, store=False)

    custodial_relationship_ids = fields.Many2many(
        'school_base.relationship', string="Custody contacts",
        compute="compute_self_relationship_ids", store=False)

    relationship_members_ids = fields.One2many(
        "school_base.relationship", "family_id",
        string="Relationships Members", readonly=True)
    homeroom = fields.Char("Homeroom")
    class_year = fields.Char("Class year")
    student_sub_status_id = fields.Many2one(
        'school_base.enrollment.sub_status', string="Sub status")

    enrolled_date = fields.Date(string="Enrolled date")
    graduation_date = fields.Date(string="Graduation date")

    withdraw_date = fields.Date(string="Withdraw date")
    withdraw_reason_id = fields.Many2one('school_base.withdraw_reason',
                                         string="Withdraw reason")

    reenrollment_record_ids = fields.One2many(
        'school_base.reenrollment.record', 'partner_id')

    reenrollment_status_id = fields.Selection(
        SELECT_REENROLLMENT_STATUS, string="Reenrollment Status", store=True,
        compute='_compute_reenrollment_status')
    reenrollment_school_year_id = fields.Many2one(
        'school_base.school_year', string="Reenollment school year", store=True,
        compute='_compute_reenrollment_status')

    placement_id = fields.Many2one(
        'school_base.placement', string="Placement")
    # - Finance
    financial_res_ids = fields.Many2many(
        "res.partner",
        string="Financial responsability",
        relation="partner_financial_res",
        column1="partner_id",
        column2="partner_financial_id")

    # - Others
    facts_approved = fields.Boolean()
    company_type = fields.Selection(
        SELECT_COMPANY_TYPES, string="Company Type")
    person_type = fields.Selection(SELECT_PERSON_TYPES, string="Person Type")
    comment_facts = fields.Text("Facts Comment")
    facts_id_int = fields.Integer("Facts id (Integer)")
    facts_id = fields.Char("Facts id")

    # Facts UDID
#     facts_udid_int = fields.Integer(
#         "Facts UDID (Integer)", compute="_converts_facts_udid_id_to_int",
#         store=True, readonly=True)
    facts_udid = fields.Char("Facts UDID")

    # Enrollment history
    enrollment_history_ids = fields.One2many(
        'school_base.enrollment.history', 'student_id')

    ##############################
    # Compute and search methods #
    ##############################
    @api.depends('school_grade_ids')
    def compute_grade_levels(self):
        for partner_id in self:
            partner_id.grade_level_ids =\
                partner_id.mapped('school_grade_ids.grade_level_id')

    @api.depends("allow_edit_student_name", "allow_edit_parent_name",
                 "allow_edit_person_name", "person_type")
    def _compute_allow_name_edition(self):
        for partner_id in self:
            # Sumulating switch statement
            partner_id.is_name_edit_allowed = switch_statement(cases={
                "default": partner_id.allow_edit_person_name,
                "parent": partner_id.allow_edit_parent_name,
                "student": partner_id.allow_edit_student_name,
                }, value=partner_id.person_type)

    @api.depends("facts_id")
    def _converts_facts_id_to_int(self):
        for partner_id in self:
            partner_id.facts_id_int = int(partner_id.facts_id) if partner_id.facts_id and partner_id.facts_id.isdigit() else 0

#     @api.depends("facts_udid")
#     def _converts_facts_udid_id_to_int(self):
#         for partner_id in self:
#             partner_id.facts_udid_int = int(
#                 partner_id.facts_udid) if partner_id.facts_udid and partner_id.facts_udid.isdigit() else 0

#     @api.depends("facts_udid")
#     def _converts_facts_udid_id_to_int(self):
#         for partner_id in self:
#             partner_id.facts_udid_int = int(
#                 partner_id.facts_udid) if partner_id.facts_udid and partner_id.facts_udid.isdigit() else 0

    @api.depends("first_name", "middle_name", "last_name")
    def _compute_name(self):
        self.auto_format_name()

    @api.depends('reenrollment_record_ids')
    def _compute_reenrollment_status(self):
        for partner_id in self:
            reenrollment_record_id = partner_id.reenrollment_record_ids.sorted('create_date', reverse=True)[:1]
            partner_id.reenrollment_school_year_id = reenrollment_record_id.school_year_id.id
            partner_id.reenrollment_status_id = reenrollment_record_id.reenrollment_status

    def compute_self_relationship_ids(self):
        for partner_id in self:
            partner_id.self_relationship_ids = \
                partner_id.family_ids.mapped('member_relationship_ids')\
                    .filtered_domain([
                        ('partner_individual_id', '=', partner_id.id),
                        ('partner_individual_id.active', '=', True),
                        ('partner_relation_id.active', '=', True),
                        ])

            parent_types = ['parent', 'father', 'mother']
            sibling_types = ['brother', 'sister', 'sibling']

            parent_ids = partner_id.self_relationship_ids.filtered_domain([
                ('relationship_type_id.type', 'in', parent_types)
                ])
            sibling_ids = partner_id.self_relationship_ids.filtered_domain([
                ('relationship_type_id.type', 'in', sibling_types)
                ])
            other_ids = partner_id.self_relationship_ids \
                .filtered_domain([
                ('relationship_type_id.type', 'not in'
                 , parent_types + sibling_types)
                ])

            custody_ids = partner_id.self_relationship_ids.filtered('custody')

            partner_id.parent_relationship_ids = parent_ids
            partner_id.sibling_relationship_ids = sibling_ids
            partner_id.other_relationship_ids = other_ids
            partner_id.custodial_relationship_ids = custody_ids

    ############################
    # Constrains and onchanges #
    ############################
    @api.onchange('school_code_ids')
    def onchange_school_code_ids(self):
        for partner_id in self:
            # We remove all
            school_code_ids = partner_id.school_code_ids._origin

            # Add those which aren't in the list
            school_codes_to_add = (
                    school_code_ids
                    - partner_id.school_grade_ids.mapped('school_code_id'))

            # Remove those that aren't in the school codes list
            school_codes_to_remove = (
                    partner_id.school_grade_ids.mapped('school_code_id')
                    - school_code_ids)

            records_to_remove = partner_id.school_grade_ids.filtered(
                lambda school_grade:
                    school_grade.school_code_id in school_codes_to_remove)

            # We add news
            self.env['school_base.partner_school_grade'].create([{
                'school_code_id': school_code.id,
                'partner_id': partner_id.id,
                'grade_level_id': False
                } for school_code in school_codes_to_add])

            partner_id.school_grade_ids -= records_to_remove

    @api.onchange("person_type")
    def _onchange_person_type(self):
        self._compute_allow_name_edition()

    @api.onchange('parent_id', 'home_address_id',
                  'home_address_country_id',
                  'home_address_state_id',
                  'home_address_city',
                  'home_address_street',
                  'home_address_street2',
                  'home_address_phone',
                  )
    def onchange_parent_id(self):
        res = super(ResPartner, self).onchange_parent_id()
        res = res or {}
        if self.home_address_id:
            address_fields = self._address_fields()
            if any(self.home_address_id[key] for key in address_fields):
                def convert(value):
                    return value.id if isinstance(value, models.BaseModel) else value
                res['value'] = {key: convert(self.home_address_id[key]) for key in address_fields}
        return res

    @api.onchange('home_address_id', 'home_address_phone')
    def _phone_sync_from_home_address(self):
        for partner in self:
            if partner.home_address_id.phone:
                partner.phone = partner.home_address_id.phone

#     @api.constrains("facts_udid")
#     def _check_facts_udid_id(self):
#         for partner_id in self:
#             if partner_id.facts_udid:

#                 if not partner_id.facts_udid.isdigit():
#                     raise ValidationError("Facts id needs to be an number")

#                 should_be_unique = self.search_count([("facts_id", "=", partner_id.facts_udid)])
#                 if should_be_unique > 1:
#                     raise ValidationError("Another contact has the same facts udid! (%s)" % partner_id.facts_udid)

    @api.constrains("facts_id")
    def _check_facts_id(self):
        for partner_id in self:
            if partner_id.facts_id:
                if not partner_id.facts_id.isdigit():
                    raise ValidationError("Facts id needs to be an number")

                should_be_unique = self.search_count(
                    [("facts_id", "=", partner_id.facts_id),
                     ('is_family', '=', partner_id.is_family)])
                if should_be_unique > 1:
                    raise ValidationError(
                        "Another contact has the same facts id! (%s)" % partner_id.facts_id)

    @api.onchange("first_name", "middle_name", "last_name")
    def _onchange_name_fields(self):
        self.auto_format_name()

    @api.constrains('member_relationship_ids')
    def _constrains_member_relationship_ids(self):
        for partner in self:
            rel_ids_pairs = (
                partner.member_relationship_ids
                    .filtered(lambda r: r.partner_relation_id.active and r.partner_individual_id.active)
                    .mapped(lambda rel: (rel.partner_individual_id.id, rel.partner_relation_id.id))
            )
            for rel_pair in rel_ids_pairs:
                if rel_ids_pairs.count(rel_pair) > 1:
                    raise UserError(_("Duplicated member relationships is not supported"))
    #########################
    # CRUD method overrides #
    #########################
    @api.model
    def create(self, values):
        """ Student custom creation for family relations and other stuffs """

        # Some constant for making more readeable the code
        # ACTION_TYPE = 0
        # TYPE_REPLACE = 6
        TYPE_ADD_EXISTING = 4
        # TYPE_REMOVE_NO_DELETE = 3

        if "name" not in values:
            first_name = values["first_name"] if "first_name" in values else ""
            middle_name = values[
                "first_name"] if "middle_name" in values else ""
            last_name = values["last_name"] if "last_name" in values else ""

            values["name"] = self.format_name(first_name, middle_name,
                                              last_name)
        partners = super().create(values)

        partners.check_school_fields_integrity(values)

        ctx = self._context
        for record in partners:
            if "member_id" in ctx:
                if ctx.get("member_id"):
                    record.write({
                        "member_ids": [
                            [TYPE_ADD_EXISTING, ctx.get("member_id"), False]]
                        })
                else:
                    raise UserError(
                        _("Contact should be save before adding families"))

        return partners

    def write(self, values):
        """ Student custom creation for family relations and other stuffs """

        # Some constant for making more readeable the code
        ACTION_TYPE = 0
        TYPE_CREATE = 0
        TYPE_REPLACE = 6
        TYPE_ADD_EXISTING = 4
        TYPE_REMOVE_NO_DELETE = 3
        TYPE_REMOVE_DELETE = 2

        for partner_id in self:
            if "family_ids" in values:
                for m2m_action in values["family_ids"]:
                    if m2m_action[ACTION_TYPE] == TYPE_REPLACE:
                        family_ids = self.browse(m2m_action[2])
                        removed_family_ids = partner_id.family_ids - family_ids
                        new_family_ids = family_ids - partner_id.family_ids

                        # Adding myself as a family's member

                        for family_id in new_family_ids:
                            new_relationship_values = []
                            for member in family_id.member_ids:
                                if not family_id.member_relationship_ids.filtered(lambda r: r.partner_individual_id == member and r.partner_relation_id == partner_id):
                                    new_relationship_values.append((TYPE_CREATE, 0, {
                                        'partner_individual_id': member.id,
                                        'partner_relation_id': partner_id.id,
                                        }))
                                if not family_id.member_relationship_ids.filtered(lambda r: r.partner_individual_id == partner_id and r.partner_relation_id == member):
                                    new_relationship_values.append((TYPE_CREATE, 0, {
                                        'partner_individual_id': partner_id.id,
                                        'partner_relation_id': member.id,
                                        }))

                            family_id.write({
                                'member_ids': [[TYPE_ADD_EXISTING, partner_id.id, False]],
                                'member_relationship_ids': new_relationship_values,
                                })

                        # Removing myself as a family's member
                        relations_to_remove = \
                            removed_family_ids.member_relationship_ids \
                                .filtered_domain([
                                '|',
                                ('partner_individual_id', '=', partner_id.id),
                                ('partner_relation_id', '=', partner_id.id)
                                ])

                        removed_family_ids.write({
                            'member_ids': [[TYPE_REMOVE_NO_DELETE, partner_id.id, False]],
                            'member_relationship_ids': [(TYPE_REMOVE_DELETE, relation.id, 0) for relation in relations_to_remove],
                            })

            if "member_ids" in values:
                for m2m_action in values["member_ids"]:
                    if m2m_action[ACTION_TYPE] == TYPE_REPLACE:
                        member_ids = self.browse(set(m2m_action[2]))
                        removed_member_ids = partner_id.member_ids - member_ids

                        # Adding myself as a family of the member
                        member_ids.write({
                            "family_ids": [
                                (TYPE_ADD_EXISTING, partner_id.id, False)],
                            })
                        new_member_ids = member_ids - partner_id.member_ids
                        relationship_values = values.get('member_relationship_ids', [])
                        for new_member_id in new_member_ids:
                            for member in member_ids.filtered(lambda m: m != new_member_id):
                                if not partner_id.member_relationship_ids.filtered(lambda m: m.partner_individual_id == member and m.partner_relation_id == new_member_id):
                                    relationship_values.append((TYPE_CREATE, 0, {
                                        'partner_individual_id': member.id,
                                        'partner_relation_id': new_member_id.id,
                                        }))
                                if not partner_id.member_relationship_ids.filtered(lambda m: m.partner_relation_id == member and m.partner_individual_id == new_member_id):
                                    relationship_values.append((TYPE_CREATE, 0, {
                                        'partner_individual_id': new_member_id.id,
                                        'partner_relation_id': member.id,
                                        }))

                        # Remove duplicated
                        no_duplicated = set(map(lambda rel: (rel[0], rel[1], tuple(rel[2].items())), relationship_values))
                        relationship_values = list(map(lambda rel: (rel[0], rel[1], dict(rel[2])), no_duplicated))

                        # Removing myself as a family of the member
                        relations_to_remove = \
                            partner_id.member_relationship_ids \
                                .filtered_domain([
                                '|',
                                ('partner_individual_id', 'in', removed_member_ids.ids),
                                ('partner_relation_id', 'in', removed_member_ids.ids)
                                ])
                        removed_member_ids.write({
                            "family_ids": [
                                [TYPE_REMOVE_NO_DELETE, partner_id.id, False]],
                            })
                        relationship_values.extend([
                            (TYPE_REMOVE_DELETE, relation.id, 0)
                            for relation in relations_to_remove])
                        values['member_relationship_ids'] = relationship_values

        res = super().write(values)
        # self.generate_missing_relationships
        self.check_school_fields_integrity(values)
        return res

    ##################
    # Action methods #
    ##################

    ####################
    # Business methods #
    ####################

    # Overwritten fields
    # Name should be readonly
    def _retrieve_allow_name_edit_from_config(self):
        self.allow_edit_student_name = bool(
            self.env["ir.config_parameter"].sudo().get_param("school_base.allow_edit_student_name", False))
        self.allow_edit_parent_name = bool(
            self.env["ir.config_parameter"].sudo().get_param("school_base.allow_edit_parent_name", False))
        self.allow_edit_person_name = bool(
            self.env["ir.config_parameter"].sudo().get_param("school_base.allow_edit_person_name", False))

    def _fields_sync(self, values):
        super(ResPartner, self)._fields_sync(values)
        if values.get('home_address_id'):
            self._phone_sync_from_home_address()
            onchange_vals = self.onchange_parent_id().get('value', {})
            self.update_address(onchange_vals)

    @api.model
    def format_name(self, first_name, middle_name, last_name):
        """
        This will format everything depending of school base settings
        :return: A String with the formatted version
        """

        name_order_relation = {
            self.env.ref(
                "school_base.name_sorting_first_name"): first_name or "",
            self.env.ref(
                "school_base.name_sorting_middle_name"): middle_name or "",
            self.env.ref("school_base.name_sorting_last_name"): last_name or ""
            }

        name_sorting_ids = self.env.ref(
            "school_base.name_sorting_first_name") + \
                           self.env.ref(
                               "school_base.name_sorting_middle_name") + \
                           self.env.ref("school_base.name_sorting_last_name")

        name = ""
        sorted_name_sorting_ids = name_sorting_ids.sorted("sequence")
        for sorted_name_id in sorted_name_sorting_ids:
            name += (sorted_name_id.prefix or "") + \
                    name_order_relation.get(sorted_name_id, "") + \
                    (sorted_name_id.sufix or "")

        return name

    def auto_format_name(self):
        """ Use format_name method to create that """
        # partner_ids = self.filtered(lambda partner: partner_id)
        for partner_id in self:
            first = partner_id.first_name
            middle = partner_id.middle_name
            last = partner_id.last_name

            if not partner_id.is_company and not partner_id.is_family and any(
                    [first, middle, last]):
                # old_name = partner_id.name
                partner_id.name = partner_id.format_name(first, middle, last)
            else:
                partner_id.name = partner_id.name

    def _set_parent_relationships(self):
        """ If you remove someone as parents
            Normally you expect that the person still belong to the family
            So, we just change"""
        for partner_id in self:
            parent_types = ['parent', 'father', 'mother']
            family_ids = partner_id.mapped('parent_relationship_ids.family_id')

            default_parent_type = \
                self.env['school_base.relationship_type'].search([
                    ('type', 'in', parent_types)
                    ])[:1]

            def filter_parent(relationship):
                return relationship.filtered_domain([
                    ('relationship_type_id.type', 'in', parent_types),
                    ('partner_individual_id', '=', partner_id.id),
                    ('partner_individual_id.active', '=', True),
                    ('partner_relation_id.active', '=', True),
                    ])

            for family_id in partner_id.family_ids:
                family_relations = filter_parent(family_id.member_relationship_ids)
                rel_to_remove = family_relations - partner_id.parent_relationship_ids
                rel_to_add = partner_id.parent_relationship_ids.filtered(lambda r: r.family_id == family_id and r not in family_id.member_relationship_ids)

                for parent in rel_to_add:
                    if not parent.relationship_type_id.type:
                        parent.relationship_type_id = default_parent_type
                    if parent.partner_individual_id != partner_id:
                        parent.partner_individual_id = partner_id

                    family_id.sudo().member_relationship_ids += parent

                    # Add as family member if it's new
                    if parent.partner_relation_id not in family_id.member_ids:
                        family_id.member_ids += parent.partner_relation_id

                # family_id.member_relationship_ids -= rel_to_remove
                rel_to_remove.write({'relationship_type_id': False})

    def _set_sibling_relationships(self):
        for partner_id in self:
            sibling_types = ['sibling', 'father', 'mother']
            default_sibling_type = \
                self.env['school_base.relationship_type'].search([
                    ('type', 'in', sibling_types)
                    ])[:1]

            family_ids = partner_id.mapped('sibling_relationship_ids.family_id')

            def filter_sibling(relationship):
                return relationship.filtered_domain([
                    ('relationship_type_id.type', 'in', sibling_types),
                    ('partner_individual_id', '=', partner_id.id),
                    ('partner_individual_id.active', '=', True),
                    ('partner_relation_id.active', '=', True),
                    ])

            for family_id in partner_id.family_ids:
                family_relations = filter_sibling(family_id.member_relationship_ids)
                rel_to_remove = family_relations - partner_id.sibling_relationship_ids
                rel_to_add = partner_id.sibling_relationship_ids.filtered(lambda r: r.family_id == family_id and r not in family_id.member_relationship_ids)

                for sibling in rel_to_add:
                    if not sibling.relationship_type_id.type:
                        sibling.relationship_type_id = default_sibling_type
                    if sibling.partner_individual_id != partner_id:
                        sibling.partner_individual_id = partner_id

                    family_id.sudo().member_relationship_ids += sibling

                    # Add as family member if it's new
                    if sibling.partner_relation_id not in family_id.member_ids:
                        family_id.member_ids += sibling.partner_relation_id

                rel_to_remove.write({'relationship_type_id': False})

    def _set_other_relationships(self):
        for partner_id in self:
            other_types = [
                'sibling', 'father', 'mother', 'parent', 'father', 'mother'
                ]
            other_ids = partner_id.other_relationship_ids

            def filter_other(relationship):
                return relationship.filtered_domain([
                    ('relationship_type_id.type', 'not in', other_types),
                    ('partner_individual_id', '=', partner_id.id),
                    ('partner_individual_id.active', '=', True),
                    ('partner_relation_id.active', '=', True),
                    ])

            for family_id in partner_id.family_ids:
                family_relations = filter_other(
                    family_id.member_relationship_ids)
                rel_to_remove = family_relations - other_ids
                rel_to_add = other_ids.filtered(lambda r: r.family_id == family_id and r not in family_id.member_relationship_ids)
                
                for other in rel_to_add:
                    if other.partner_individual_id != partner_id:
                        other.partner_individual_id = partner_id

                    family_id.sudo().member_relationship_ids += other

                    # Add as family member if it's new
                    if other.partner_relation_id not in family_id.member_ids:
                        family_id.member_ids += other.partner_relation_id
                rel_to_remove.mapped('partner_relation_id').active = False

    def generate_missing_relationships(self):
        for family_id in self.filtered('is_family'):
            relationship_values = []
            for member in family_id.member_ids:
                for aux_member in family_id.member_ids.filtered(lambda m: m != member):
                    if not family_id.member_relationship_ids.filtered(
                            lambda m: m.partner_individual_id == member and m.partner_relation_id == aux_member):
                        relationship_values.append((0, 0, {
                            'partner_individual_id': member.id,
                            'partner_relation_id': aux_member.id,
                            }))
                    if not family_id.member_relationship_ids.filtered(
                            lambda m: m.partner_relation_id == aux_member and m.partner_individual_id == member):
                        relationship_values.append((0, 0, {
                            'partner_individual_id': aux_member.id,
                            'partner_relation_id': member.id,
                            }))
            if relationship_values:
                no_duplicated = set(map(lambda rel: (rel[0], rel[1], tuple(rel[2].items())), relationship_values))
                relationship_values = list(map(lambda rel: (rel[0], rel[1], dict(rel[2])), no_duplicated))
                family_id.write({'member_relationship_ids': relationship_values})

    def check_school_fields_integrity(self, values={}):
        for partner in self:
            # Email constraint
            if 'email' in values:
                if (partner.is_family
                        or partner.person_type
                        or partner.member_ids
                        or partner.family_ids):
                    # Email check
                    if partner.email:
                        email_partner = self.search([
                            '&',
                            ('email', '=', partner.email),
                            '|', '|', '|',
                            ('is_family', '=', True),
                            ('person_type', '!=', False),
                            ('member_ids', '!=', False),
                            ('family_ids', '!=', False),
                            ])
                        if email_partner and (len(email_partner) > 1 or email_partner != partner):
                            raise UserError(_(
                                "There is other existing family with the same"
                                " email address, please, use another one"))

    # Helpers methods
    # devuelve familias de un partner
    def get_families(self):
        PartnerEnv = self.env["res.partner"].sudo()
        return PartnerEnv.search([("is_family", "=", True)]).filtered(
            lambda app: self.id in app.member_ids.ids)

    def set_member_relationship(self, individual_id: int, relation_id: int, reltype_id: int = False):
        self.ensure_one()
        if not self.is_family:
            raise UserError("You only can modify member relationship from families")

        relationship = \
            self.member_relationship_ids.filtered(
                lambda rel:
                    rel.partner_individual_id.id == individual_id
                    and rel.partner_relation_id.id == relation_id)

        if not relationship:
            relationship = self.env['school_base.relationship'].create({
                'partner_individual_id': individual_id,
                'partner_relation_id': relation_id,
                'family_id': self.id
                })
        relationship.relationship_type_id = reltype_id
        return relationship
