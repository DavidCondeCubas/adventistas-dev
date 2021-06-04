# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrderReconcilePaymentWizard(models.TransientModel):
    ######################
    # Private attributes #
    ######################
    _name = "sale.order.reconcile.payment.wizard"

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    sale_order_id = fields.Many2one(string="Sales Order",
        comodel_name="sale.order")
    payment_id = fields.Many2one(string="Payment Record",
        comodel_name="sale.order.payment")
    amount_to_reconcile = fields.Float(string="Amount to Pay",
        required=True)
    date_reconciled = fields.Date(string="Date", 
        default=lambda _: fields.Date.today())

    ##############################
    # Compute and search methods #
    ##############################

    ############################
    # Constrains and onchanges #
    ############################
    @api.constrains("amount_to_reconcile")
    def _check_amount_to_pay(self):
        for record in self:
            if record.amount_to_reconcile <= 0:
                raise ValidationError("Amount to Reconcile should not be 0.")

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
        reconciled_payment = so_payment_reconcile_obj.create(payment_reconcile_values)
        reconciled_payment._create_account_payment()

    ####################
    # Business methods #
    ####################