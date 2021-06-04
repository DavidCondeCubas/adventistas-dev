# -*- coding: utf-8 -*-

from odoo import models, fields


class SchoolBaseSchoolYear(models.Model):
    _inherit = 'school_base.school_year'

    active_admissions = fields.Boolean()
    # active_school_year_ids = fields.Many2many('school_base.school_year')


class SchoolBaseGradeLevel(models.Model):
    _inherit = 'school_base.grade_level'

    active_admissions = fields.Boolean()
    # active_school_code_ids = fields.Many2many('school_base.school_year')
