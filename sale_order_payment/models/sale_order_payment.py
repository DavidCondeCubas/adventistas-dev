# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SaleOrderPayment(models.Model):
    ######################
    # Private attributes #
    ######################
    _name = "sale.order.payment"
    _rec_name = "id"

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    state = fields.Selection(string="State",
        selection=[("valid", "Valid"), ("cancelled", "Cancelled")],
        default="valid")
    partner_id = fields.Many2one(string="Customer",
        comodel_name="res.partner")
    currency_id = fields.Many2one(string="Currency",
        comodel_name="res.currency")
    journal_id = fields.Many2one(string="Journal",
        comodel_name="account.journal",
        domain="[('type','in',['bank','cash'])]")
    reconciled_payment_ids = fields.One2many(string="Reconciliations",
        inverse_name="payment_id",
        comodel_name="sale.order.payment.reconcile")
    payment_date = fields.Date(string="Date", 
        default=lambda _: fields.Date.today(),
        required=True)
    memo = fields.Char(string="Memo")
    amount_paid = fields.Monetary(string="Amount Paid")
    reconcilable_amount = fields.Monetary(string="Reconcilable Amount",
        compute="_compute_reconcilable_amount",
        store=True)

    ##############################
    # Compute and search methods #
    ##############################
    @api.depends("reconciled_payment_ids", "amount_paid")
    def _compute_reconcilable_amount(self):
        for record in self:
            amount = record.amount_paid

            for reconciled_payment in record.reconciled_payment_ids:
                amount -= reconciled_payment.amount_reconciled

            record.reconcilable_amount = amount

    ############################
    # Constrains and onchanges #
    ############################

    #########################
    # CRUD method overrides #
    #########################

    ##################
    # Action methods #
    ##################
    def action_reconcile(self):
        sale_order = self.env["sale.order"].browse(self._context.get("sale_order_id"))

        if not sale_order:
            raise ValidationError("No sale order found.")

        wizard_obj = self.env["sale.order.reconcile.payment.wizard"]
        wizard = wizard_obj.create({
            "sale_order_id": sale_order.id,
            "payment_id": self.id,
            "amount_to_reconcile": sale_order.amount_due_after_reconcile
        })

        return {
            "name": "Sales Order Reconcile Payment Wizard",
            "view_mode": "form",
            "view_type": "form",
            "target": "new",
            "res_model": "sale.order.reconcile.payment.wizard",
            "type": "ir.actions.act_window",
            "domain": "[]",
            "res_id": wizard.id,
        }

    def action_cancel(self):
        self.ensure_one()
        if self.reconciled_payment_ids.filtered(lambda p: p.account_payment_id.exists()):
            raise ValidationError("You can't cancel a sales order payment with a related invoice payment.")
        self.state = "cancelled"
        self.reconciled_payment_ids.unlink()

    def action_reset_to_valid(self):
        self.ensure_one()
        self.state = "valid"

    ####################
    # Business methods #
    ####################
    def _prepare_account_payment_values(self, payment_method_id=None, payment_type="inbound", partner_id=None, amount=None, journal_id=None):
        self.ensure_one()

        if not payment_method_id:
            payment_method_id = self.env["account.payment.method"].search([
                ("name", "=", "Manual"), ("payment_type", "=", "inbound")
            ]).id

        return {
            "payment_type": payment_type,
            "partner_type": "customer",
            "partner_id": self.partner_id.id if not partner_id else partner_id,
            "amount": self.amount_paid if not amount else amount,
            "journal_id": self.journal_id.id if not journal_id else journal_id,
            "payment_method_id": payment_method_id
        }

    def _prepare_reconcile_values(self, sale_order_id, amount_reconciled, payment_id=None):
        self.ensure_one()
        
        return {
            "sale_order_id": sale_order_id,
            "amount_reconciled": amount_reconciled,
            "payment_id": self.id if not payment_id else payment_id
        }