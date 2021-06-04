# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    ######################
    # Private attributes #
    ######################
    _inherit = "sale.order"

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    @api.depends("amount_due_after_reconcile")
    def _compute_remaining_amount(self):
        for so in self:
            invoices = so.invoice_ids.filtered(lambda x: x.type in ["out_invoice", "out_receipt"] and x.state != "cancel")
            remaining_amount = so.amount_due_after_reconcile - sum(invoices.mapped("amount_total"))
            so.remaining_amount = max(remaining_amount, 0)


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
