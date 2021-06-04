# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrderReconcilePaymentWizard(models.TransientModel):
    ######################
    # Private attributes #
    ######################
    _inherit = "sale.order.reconcile.payment.wizard"

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
    def action_reconcile_payment(self):
        self.ensure_one()

        so_payment_reconcile_obj = self.env["sale.order.payment.reconcile"]

        if self.amount_to_reconcile > self.payment_id.reconcilable_amount:
            raise ValidationError("Amount to Reconcile should not be greater than the related Payment's amount.")

        payment_reconcile_values = self.payment_id._prepare_reconcile_values(self.sale_order_id.id, self.amount_to_reconcile)  
        wallet = self.payment_id.wallet_id

        if wallet:
            invoice_lines = [(0, 0, {
                "product_id": wallet.product_id.id,
                "account_id": wallet.account_id.id,
                "price_unit": self.amount_to_reconcile,
                "quantity": 1
            })]
            credit_note_values = self.sale_order_id._prepare_credit_note_values(
                wallet.journal_category_id.id, invoice_lines, partner_id=self.payment_id.partner_id.id)
            credit_note = self.env["account.move"].create(credit_note_values)
            credit_note.action_post()

            payment_reconcile_values.update({
                "credit_note_id": credit_note.id
            })
        
        reconciled_payment = so_payment_reconcile_obj.create(payment_reconcile_values)

        if not wallet:
            reconciled_payment._create_account_payment()

    ####################
    # Business methods #
    ####################
