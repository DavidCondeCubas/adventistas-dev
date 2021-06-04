# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleOrderPaymentReconcile(models.Model):
    ######################
    # Private attributes #
    ######################
    _name = "sale.order.payment.reconcile"

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    currency_id = fields.Many2one(string="Currency",
                                  comodel_name="res.currency",
                                  related="sale_order_id.currency_id")
    sale_order_id = fields.Many2one(string="Sales Order",
                                    readonly=True,
                                    required=True,
                                    ondelete="cascade",
                                    comodel_name="sale.order")
    payment_id = fields.Many2one(string="Payment",
                                 required=True,
                                 readonly=True,
                                 ondelete="cascade",
                                 comodel_name="sale.order.payment")
    account_payment_id = fields.Many2one(string="Related Invoice Payment",
                                         comodel_name="account.payment")
    amount_reconciled = fields.Monetary(string="Amount Reconciled")
    date_reconciled = fields.Date(string="Date",
                                  default=lambda _: fields.Date.today(),
                                  required=True)

    ##############################
    # Compute and search methods #
    ##############################

    ############################
    # Constrains and onchanges #
    ############################

    #########################
    # CRUD method overrides #
    #########################
    @api.model
    def create(self, vals):
        res = super(SaleOrderPaymentReconcile, self).create(vals)

        for record in res:
            so = record.sale_order_id
            
            if self.env.company.create_invoice_on_so_fully_paid_enabled and so.amount_due_after_reconcile <= 0:
                invoice = record.sale_order_id._create_invoices()
                so._create_invoice_with_reconciliation(invoice_id=invoice.id)

        return res

    ##################
    # Action methods #
    ##################
    def action_unreconcile(self):
        for record in self:
            payment = record.account_payment_id
            if payment:
                if payment.reconciled_invoice_ids.exists():
                    raise UserError(
                        "Cannot unreconcile a payment with a related Invoice Payment.")
                
                payment.action_draft()
                payment.cancel()
                
            record.unlink()

    ####################
    # Business methods #
    ####################
    def _create_account_payment(self):
        self.ensure_one()

        account_payment = self.env["account.payment"]

        if not self.account_payment_id:
            account_payment_values = self.payment_id._prepare_account_payment_values()
            account_payment = self.env["account.payment"].create(account_payment_values)
            self.account_payment_id = account_payment.id

        if account_payment.state == "draft":
            account_payment.post()

        return self.account_payment_id

