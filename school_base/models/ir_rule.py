# coding: utf-8
from odoo import api, models
from odoo.addons.website.models import ir_http


class IrRule(models.Model):
    _inherit = 'ir.rule'

    @api.model
    def _eval_context(self):
        res = super(IrRule, self)._eval_context()
        res.update({
            'district_code_id': self.env.district_code.id,
            'district_code_ids': self.env.district_codes.ids,
            'school_code_id': self.env.school_code.id,
            'school_code_ids': self.env.school_codes.ids,
            })
        return res

    def _compute_domain_keys(self):
        """ Return the list of context keys to use for caching
         ``_compute_domain``. """
        return super(IrRule, self)._compute_domain_keys() \
               + ['allowed_school_code_ids', 'allowed_district_code_ids']