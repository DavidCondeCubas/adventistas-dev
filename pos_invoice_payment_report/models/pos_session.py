# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PosSession(models.Model):
    ######################
    # Private attributes #
    ######################
    _inherit = "pos.session"

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################

    ##############################
    # Compute and search methods #
    ##############################
    @api.depends("invoice_payment_amount")
    def _compute_consolidated_payments_amount(self):
        super(PosSession, self)._compute_consolidated_payments_amount()
        for record in self:
            record.consolidated_payments_amount += record.invoice_payment_amount

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