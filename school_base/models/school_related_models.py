# -*- coding: utf-8 -*-

"""
Author: Luis Malavé
Date: 2021-04-05
Yes, I know that Odoo tips say dont do this...
But... I am just grouping things together to get some kind of order without
modifying the __init__ over and over again...
"""

from odoo import models, fields, api, _
import datetime

from odoo.exceptions import UserError


class DistrictCode(models.Model):
    """ District code """
    _name = "school_base.district_code"
    _description = "District code"
    _order = "sequence"

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(default=1)
    school_code_ids = fields.One2many("school_base.school_code", "district_code_id", string="School code")


class SchoolCode(models.Model):
    _name = "school_base.school_code"
    _order = "sequence"
    _description = "School code"
    _rec_name = 'display_name'

    name = fields.Char(string="code", required=True)
    display_name = fields.Char(readonly=True, compute='_compute_display_name', store=True)
    description = fields.Char("Description")
    school_name = fields.Char(string="School name")
    sequence = fields.Integer(default=1)
    district_code_id = fields.Many2one("school_base.district_code", "District Code")
    grade_level_ids = fields.One2many("school_base.grade_level", 'school_code_id')

    @api.depends('name', 'description')
    def _compute_display_name(self):
        for school_code_id in self:
            school_code_id.display_name = "%s - (%s)" % (school_code_id.name, school_code_id.description)


class SchoolYear(models.Model):
    _name = "school_base.school_year"
    _order = "sequence"
    _description = "School year"

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(default=1)
    facts_id = fields.Integer("Facts ID", readonly=True)
    active_admissions = fields.Boolean('Active admissions')
    school_code_id = fields.Many2one("school_base.school_code", string="School code")
    district_code_id = fields.Many2one(related="school_code_id.district_code_id")

    date_start = fields.Date(required=True, default=datetime.datetime.now().date())
    date_end = fields.Date(required=True, default=datetime.datetime.now().date())

    @api.constrains('date_start', 'date_end')
    def _check_date_ranges(self):
        for school_year_id in self:
            school_year_ids = self.search([
                ('school_code_id', '=', school_year_id.school_code_id.id),
                ('id', '!=', school_year_id.id)
            ])

            # Collision detection
            for other_school_year_id in school_year_ids:
                if (school_year_id.date_end < other_school_year_id.date_start
                        or school_year_id.date_start > other_school_year_id.date_end):
                    continue
                else:
                    raise UserError(
                        _("Date range collision detected between %s and %s school years in %s school code")
                        % (school_year_id.name, other_school_year_id.name, school_year_id.school_code_id.name))

    @api.onchange('school_code_id')
    def _get_school_code_id_domain(self):
        self.ensure_one()
        school_code_ids = self.district_code_id.school_code_ids.ids
        return {'domain': {'school_code_id': [('id', 'in', school_code_ids)]}}


class GradeLevel(models.Model):
    _name = "school_base.grade_level"
    _order = "sequence"
    _description = "The grade level"

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(default=1)
    next_grade_level_id = fields.Many2one("school_base.grade_level", string="Next grade level")
    school_code_id = fields.Many2one("school_base.school_code", string="School code")
    district_code_id = fields.Many2one(related="school_code_id.district_code_id")
    user_type_id = fields.Many2one('school_base.grade_level.type')
    capacity = fields.Integer()

    @api.onchange('school_code_id')
    def _get_school_code_id_domain(self):
        self.ensure_one()
        school_code_ids = self.district_code_id.school_code_ids.ids
        return {'domain': {'school_code_id': [('id', 'in', school_code_ids)]}}


class SchoolBasePartnerSchoolGrade(models.Model):
    """ It is used as M:N table """

    ######################
    # Private Attributes #
    ######################
    _name = 'school_base.partner_school_grade'
    _description = "Partner school grade"

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################

    partner_id = fields.Many2one('res.partner')
    school_code_id = fields.Many2one('school_base.school_code')
    school_code_grade_level_ids = fields.One2many(
        'school_base.grade_level', related='school_code_id.grade_level_ids')
    grade_level_id = fields.Many2one('school_base.grade_level')

    ##############################
    # Compute and search methods #
    ##############################

    ############################
    # Constrains and onchanges #
    ############################

    #########################
    # CRUD method overrides #
    #########################

    ##################
    # Action methods #
    ##################

    ####################
    # Business methods #
    ####################


class SchoolBaseGradeLevelType(models.Model):
    _name = 'school_base.grade_level.type'
    _description = "Grade level type"

    type = fields.Selection(
        [
            ('elementary', _("Elementary")),
            ('middle_school', _("Middle school")),
            ('high_school', _("High school")),
        ],
        required=True
    )
    name = fields.Char(required=True)


class Placement(models.Model):
    """ An informative model for students """
    _name = 'school_base.placement'
    _description = "Placement"
    name = fields.Char(string="Placement", required=True, translate=True)
    key = fields.Char(string="Key")


class WithdrawReason(models.Model):
    """ Why does the student withdraw? """
    _name = 'school_base.withdraw_reason'
    _description = "Withdraw reasons"
    name = fields.Char(string="WithDraw Reason", required=True, translate=True)
    key = fields.Char(string="Key")


class EnrollmentStatus(models.Model):
    """ SubStatus for students """
    _name = 'school_base.enrollment.status'
    _description = "Enrollment Status"
    # status_id = fields.Selection(SELECT_STATUS_TYPES, string='Status')
    name = fields.Char(string="Name", required=True, translate=True)
    key = fields.Char(string="Key")
    note = fields.Char(string="Description")
    type = fields.Selection([
        ('admission', 'Admission'),
        ('enrolled', 'Enrolled'),
        ('graduate', 'Graduate'),
        ('inactive', 'Inactive'),
        ('pre_enrolled', 'Pre-Enrolled'),
        ('withdrawn', 'Withdrawn'),
        ])


class EnrollmentSubStatus(models.Model):
    """ SubStatus for students """
    _name = 'school_base.enrollment.sub_status'
    _description = "Enrollment sub status"

    # status_id = fields.Selection(SELECT_STATUS_TYPES, string='Status')
    # status_id = fields.Selection([('1', '1')], string='Status')
    status_id = fields.Many2one('school_base.enrollment.status', String='Status')
    name = fields.Char(string="Name", required=True, translate=True)
    key = fields.Char(string="Key")


class MaritalStatus(models.Model):
    """ An informative model for students """
    _name = 'school_base.marital_status'
    _description = "Marital Status"
    name = fields.Char(string="Name", required=True, translate=True)
    key = fields.Char(string="Key")


class Gender(models.Model):
    _name = "school_base.gender"
    _description = "School base gender"
    name = fields.Char("Gender", required=True, translate=True)
    key = fields.Char("Key")


class SchoolBaseEnrollmentHistory(models.Model):
    _name = 'school_base.enrollment.history'
    _description = "Enrollment history"
    _order = 'history_date'

    student_id = fields.Many2one('res.partner', required=True)
    school_code_id = fields.Many2one('school_base.school_code')
    school_year_id = fields.Many2one('school_base.school_year')
    grade_level_id = fields.Many2one('school_base.grade_level')

    enrollment_status_id = fields.Many2one('school_base.enrollment.status')
    enrollment_sub_status_id = fields.Many2one('school_base.enrollment.sub_status')

    note = fields.Text()
    history_date = fields.Datetime(default=datetime.datetime.now())
