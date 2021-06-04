# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleOrderPaymentReconcile(models.Model):
    ######################
    # Private attributes #
    ######################
    _inherit = "sale.order.payment.reconcile"

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    credit_note_id = fields.Many2one(comodel_name="account.move",
                                     string="Related Credit Note",
                                     readonly=True)

    ##############################
    # Compute and search methods #
    ##############################

    ############################
    # Constrains and onchanges #
    ############################

    #########################
    # CRUD method overrides #
    #########################
    def action_unreconcile(self):
        for record in self:
            payment = record.account_payment_id
            if payment:
                if payment.reconciled_invoice_ids.exists():
                    raise UserError(
                        "Cannot unreconcile a payment with a related Invoice Payment.")
                
                payment.action_draft()
                payment.cancel()
                
            credit_note = record.credit_note_id
            if credit_note:
                if credit_note.line_ids.filtered(lambda l: l.matched_credit_ids or l.matched_debit_ids):
                    raise UserError(
                        "Cannot unreconcile a payment with a Credit Note that has reconciled entries.")

                credit_note.button_draft()
                credit_note.button_cancel()

            record.unlink()

    ##################
    # Action methods #
    ##################

    ####################
    # Business methods #
    ####################