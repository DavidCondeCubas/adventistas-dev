# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    district_code_id = fields.Many2one('school_base.district_code', string="District code")
    school_code_id = fields.Many2one('school_base.school_code', string="School code")

    district_code_ids = fields.Many2many('school_base.district_code', string="District codes")
    company_district_code_ids = fields.Many2many(
        'school_base.district_code', compute='compute_company_district_codes')
    school_code_ids = fields.Many2many('school_base.school_code', string="School codes")
    company_school_code_ids = fields.Many2many('school_base.school_code',
        related='company_ids.school_code_ids')
    district_school_code_ids = fields.Many2many(
        'school_base.school_code', compute='compute_district_school_code_ids')

    @api.onchange('company_ids')
    @api.depends('company_ids')
    def compute_company_district_codes(self):
        for user in self:
            user.company_district_code_ids = user.mapped('company_ids.district_code_ids')
            
    def compute_district_school_code_ids(self):
        for user in self:
            user.district_school_code_ids = user.mapped('district_code_ids.school_code_ids')

