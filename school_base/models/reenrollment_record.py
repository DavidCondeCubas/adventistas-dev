# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SchoolBaseReenrollmentRecord(models.Model):
    _name = 'school_base.reenrollment.record'
    _description = "Reenrollment record"
    _order = 'create_date desc'

    school_year_id = fields.Many2one('school_base.school_year', required=True)
    # school_year_start_date
    next_grade_level_id = fields.Many2one('school_base.grade_level')
    reenrollment_status = fields.Selection([
                ("open", "Open"),
                ("finished", "Finished"),
                ("withdrawn", "Withdrawn"),
                ("rejected", "Rejected"),
                ("blocked", "Blocked"),
            ], string="Reenrollment Status")
    partner_id = fields.Many2one('res.partner', required=True)
    note = fields.Text()
