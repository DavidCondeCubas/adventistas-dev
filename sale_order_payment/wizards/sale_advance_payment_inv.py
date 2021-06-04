# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleAdvancePaymentInv(models.TransientModel):
    ######################
    # Private attributes #
    ######################
    _inherit = "sale.advance.payment.inv"

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    

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
    def create_invoices(self):
        res = super(SaleAdvancePaymentInv, self).create_invoices()

        sale_order = self.env["sale.order"].browse(self.env.context.get("active_ids", []))
        
        for so in sale_order:
            if so.reconciled_total > 0:
                so._create_invoice_with_reconciliation()

        return res

    ####################
    # Business methods #
    ####################