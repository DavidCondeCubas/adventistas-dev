# -*- encoding: utf-8 -*-

from ..utils import formatting

from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


class Company(models.Model):
    _inherit = "res.company"

    district_code_id = fields.Many2one("school_base.district_code", "District code")
    district_code_ids = fields.Many2many("school_base.district_code", string="District codes")
    
    district_school_code_ids = fields.Many2many(
        'school_base.school_code', compute='compute_district_school_code_ids')

    school_code_id = fields.Many2one('school_base.school_code', string="School code")
    school_code_ids = fields.Many2many(
        'school_base.school_code', string="School codes",
        store=True, compute='_compute_school_code_ids', readonly=False)
    district_code_name = fields.Char(related="district_code_id.name")
    date_sincro_contacts = fields.Datetime(help="Used to know the last time that was synchronized")

    current_school_year_id = fields.Many2one('school_base.school_year')
    enrollment_school_year_id = fields.Many2one('school_base.school_year')

    @api.depends('district_code_ids')
    def _compute_school_code_ids(self):
        for company in self:
            company.school_code_ids = company.district_code_ids.mapped('school_code_ids')

    def compute_district_school_code_ids(self):
        for company in self:
            company.district_school_code_ids = company.mapped('district_code_ids.school_code_ids')