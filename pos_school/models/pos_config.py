# -*- coding: utf-8 -*-

from odoo import models, _, api, exceptions, fields


class PosConfig(models.Model):
    """ Adds constraints """
    _inherit = "pos.config"

    is_pos_pr_discount = fields.Boolean(default=False)
    school_code_ids = fields.Many2many('school_base.school_code')
    available_school_code_ids = fields.Many2many('school_base.school_code', compute='_compute_available_school_code_ids')

    def _compute_available_school_code_ids(self):
        for session in self:
            session.available_school_code_ids = session.mapped('company_id.district_code_ids.school_code_ids')

    def open_ui(self):
        res = super(PosConfig, self).open_ui()

        res['url'] += '&school_code_ids=%s' % ','.join(map(str, self.school_code_ids.ids))

        return res

