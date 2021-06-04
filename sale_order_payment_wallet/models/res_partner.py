# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    ######################
    # Private attributes #
    ######################
    _inherit = "res.partner"

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
    def execute_autoclear(self):
        partners_with_sale_orders = self.sale_order_ids.filtered(
            lambda s: s.state == "sale" and s.invoice_payment_state != "paid").mapped("partner_id")
        partner_ids_to_apply_autoclear = super(ResPartner, self).execute_autoclear()
        partner_ids_to_apply_autoclear += partners_with_sale_orders.filtered(
            lambda p: p.id not in partner_ids_to_apply_autoclear.ids)

        for partner in partner_ids_to_apply_autoclear:
            try:
                partner.autoload_credit_notes_to_wallet()
                partner.autopay_sale_orders_with_wallet()
            except:
                raise

    def autopay_sale_orders_with_wallet(self):
        for partner in self:
            sale_orders = self.env["sale.order"].search([
                ("partner_id", "=", partner.id),
                ("state", "=", "sale"),
                ("invoice_payment_state", "!=", "paid")
            ]).filtered(lambda s: s.amount_due_after_reconcile > 0)
            sale_order_wallet_amounts = sale_orders._get_available_wallet_amounts()

            if sale_order_wallet_amounts:
                partner_wallet_amounts = sale_order_wallet_amounts[partner]
                if sum(partner_wallet_amounts.values()):
                    sale_orders.pay_with_wallet(partner_wallet_amounts)

    def get_unreconciled_credit_notes(self):
        self.ensure_one()
        credit_notes = super(ResPartner, self).get_unreconciled_credit_notes()
        return credit_notes.filtered(lambda m: not m.sale_order_payment_reconcile_id)

    ####################
    # Business methods #
    ####################
