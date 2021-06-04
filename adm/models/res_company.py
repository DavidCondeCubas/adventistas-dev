# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    mail_inviting_partner_to_application_id = fields.Many2one('mail.template')
