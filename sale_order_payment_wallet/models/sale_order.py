# -*- coding: utf-8 -*-

import logging
from collections import defaultdict

from odoo import models, fields, api
from odoo.exceptions import ValidationError

from odoo.addons.wallet.models.account_move import sort_by_wallet_hierarchy

_logger = logging.getLogger(__name__)

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
    def pay_with_wallet(self, wallet_payment_dict):
        wallet_obj = self.env["wallet.category"]
        payment_obj = self.env["sale.order.payment"]
        payment_reconcile_obj = self.env["sale.order.payment.reconcile"]

        partner = self.mapped("partner_id")
        partner.ensure_one()
        
        for so in self:
            _logger.info("Paying %s with wallet: %s" % (so.name, wallet_payment_dict))

            for wallet_id, amount in wallet_payment_dict.items():
                wallet = wallet_obj.browse(wallet_id)
                wallet_journal = wallet.journal_category_id

                amount = float(amount)
                # to make sure the payment will not be greater than the amount due
                amount = min(amount, so.amount_due_after_reconcile)
                partner_wallet_balance = wallet.get_wallet_amount(partner)
                
                if not wallet or not partner_wallet_balance:
                    if len(self) >= 2:
                        _logger.warn("Skipping Pay With Wallet: %s on Sale Order: %s, Reason: no wallet found or no wallet balance" % (wallet.name, so.name))
                        continue
                    else:
                        raise ValidationError("Error on Pay With Wallet: %s on Sale Order: %s, Reason: no wallet found or no wallet balance" % (wallet.name, so.name))

                if not amount or amount > partner_wallet_balance:
                    if len(self) >= 2:
                        _logger.warn("Skipping Pay With Wallet: %s, Sale Order %s. Reason: zero amount or amount is greater than the wallet balance." % (wallet.name, so.name))
                        continue
                    else:
                        raise ValidationError("Error on Pay With Wallet: %s, Sale Order %s. Reason: zero amount or amount is greater than the wallet balance." % (wallet.name, so.name))

                if partner_wallet_balance < -abs(wallet.credit_limit):
                    raise ValidationError("You are trying to pay %s in %s when there is only %s available") % (
                                        amount, wallet_id.name, partner_wallet_balance)
                
                
                invoice_lines = [(0, 0, {
                    "product_id": wallet.product_id.id,
                    "account_id": wallet.account_id.id,
                    "price_unit": amount,
                    "quantity": 1
                })]
                credit_note_values = self._prepare_credit_note_values(wallet_journal.id, invoice_lines, partner_id=partner.id)
                credit_note = self.env["account.move"].create(credit_note_values)
                credit_note.action_post()

                payment = payment_obj.create({
                    "partner_id": partner.id,
                    "journal_id": wallet_journal.id,
                    "wallet_id": wallet_id,
                    "amount_paid": amount,
                    "memo": so.name
                })
                payment_reconcile_values = payment._prepare_reconcile_values(so.id, amount)
                payment_reconcile_obj.create({
                    **payment_reconcile_values,
                    "credit_note_id": credit_note.id
                })

    ####################
    # Business methods #
    ####################
    def _get_wallet_paid_amounts(self):
        self.ensure_one()

        wallet_amount_to_apply = defaultdict(float)
        default_wallet = self.env.company.default_wallet_category_id

        for reconciled_payment in self.reconciled_payment_ids:
            wallet =  reconciled_payment.payment_id.wallet_id or default_wallet
            wallet_amount_to_apply[wallet] += reconciled_payment.amount_reconciled

        return dict(wallet_amount_to_apply)

    def _get_wallet_raw_due_amounts(self):
        self.ensure_one()

        order_lines = self.mapped("order_line")

        tuple_list_category_amount = order_lines.mapped(
            lambda line: (self.env["wallet.category"].get_wallet_by_category_id(line.product_id.categ_id), 
                          line.price_unit * line.product_uom_qty))

        category_amounts = defaultdict(float)

        for category_id, amount in tuple_list_category_amount:
            category_amounts[category_id] += amount

        return dict(category_amounts)
    
    def _get_wallet_due_amounts(self):
        all_wallet_due_amounts = defaultdict(float)

        for order in self:
            wallet_raw_due_amounts = order._get_wallet_raw_due_amounts()
            wallet_due_amounts = dict(wallet_raw_due_amounts)

            # Getting how much has been paid with wallets
            wallet_paid_amounts = defaultdict(float, order._get_wallet_paid_amounts())
            if wallet_paid_amounts:
                # Sorting them by wallet hierarchy, this part is crucial
                sorted_wallet_raw_due_amounts = sorted(wallet_raw_due_amounts.items(), key=sort_by_wallet_hierarchy,
                                                       reverse=True)

                for wallet_id, amount in sorted_wallet_raw_due_amounts:
                    looking_wallet = wallet_id
                    while amount > 0:
                        looking_wallet_amount = wallet_paid_amounts[looking_wallet]
                        if looking_wallet_amount > 0:
                            wallet_remove_amount = amount

                            if looking_wallet_amount - amount < 0:
                                wallet_remove_amount = looking_wallet_amount

                            wallet_paid_amounts[looking_wallet] = wallet_paid_amounts[
                                                                      looking_wallet] - wallet_remove_amount
                            amount = amount - wallet_remove_amount

                            wallet_due_amounts[wallet_id] = wallet_due_amounts[wallet_id] - wallet_remove_amount
                        if looking_wallet.is_default_wallet:
                            break
                        looking_wallet = wallet_id.get_wallet_by_category_id(looking_wallet.category_id.parent_id)

            for wallet_id, amount in wallet_due_amounts.items():
                all_wallet_due_amounts[wallet_id.id] += amount

        return all_wallet_due_amounts

    def _calculate_wallet_distribution(self, wallet_dict_to_pay, wallet_dict_available):
        wallet_dict_to_pay = { self.env["wallet.category"].browse(wallet_id): amount 
                               for wallet_id, amount in wallet_dict_to_pay.items()}
        wallet_dict_available = { self.env["wallet.category"].browse(wallet_id): amount 
                                  for wallet_id, amount in wallet_dict_available.items()}
        
        sorted_wallet_dict_to_pay = sorted(wallet_dict_to_pay.items(), key=sort_by_wallet_hierarchy, reverse=True)
        wallet_amount_to_apply = defaultdict(float)
        
        for wallet_id, amount in sorted_wallet_dict_to_pay:
            looking_wallet = wallet_id
            while amount > 0:
                if looking_wallet in wallet_dict_available:
                    looking_wallet_amount = wallet_dict_available[looking_wallet]
                    if looking_wallet_amount > -abs(wallet_id.credit_limit):
                        wallet_remove_amount = amount

                        if looking_wallet_amount - amount < -abs(looking_wallet.credit_limit):
                            wallet_remove_amount = looking_wallet_amount + abs(looking_wallet.credit_limit)

                        wallet_dict_available[looking_wallet] = wallet_dict_available[
                                                                    looking_wallet] - wallet_remove_amount
                        amount = amount - wallet_remove_amount

                        wallet_amount_to_apply[looking_wallet] = wallet_amount_to_apply[
                                                                     looking_wallet] + wallet_remove_amount

                if looking_wallet == self.env.company.default_wallet_category_id:
                    break
                looking_wallet = wallet_id.get_wallet_by_category_id(looking_wallet.category_id.parent_id)
        return dict(wallet_amount_to_apply)

    def _get_available_wallet_amounts(self):
        partner_ids_wallet_amounts = {}
        if self:
            partner_ids = self.mapped("partner_id")
            for partner_id in partner_ids:
                # sale_orders = self.filtered(lambda s: s.partner_id == partner_id).sorted(lambda s: m.invoice_date_due or m.invoice_date)
                sale_orders = self.filtered(lambda s: s.partner_id == partner_id)
                wallet_obj = self.env["wallet.category"]

                all_wallet_ids = wallet_obj.search([])
                partner_wallet_amounts = {wallet_id.id: wallet_id.get_wallet_amount(partner_id)
                                          for wallet_id in all_wallet_ids}

                wallet_to_apply = defaultdict(float)

                for sale_order in sale_orders:
                    move_wallet_amounts = sale_order._get_wallet_due_amounts()
                    amounts_to_pay = self._calculate_wallet_distribution(move_wallet_amounts, partner_wallet_amounts)

                    for wallet_id, amount in amounts_to_pay.items():
                        wallet_to_apply[wallet_id.id] += amount

                partner_ids_wallet_amounts.update({partner_id: dict(wallet_to_apply)})

        return partner_ids_wallet_amounts

    def _prepare_credit_note_values(self, journal_id, invoice_line_ids, partner_id=None):
        return {
            "type": "out_refund",
            "partner_id": self.partner_id.id if not partner_id else partner_id,
            "journal_id": journal_id ,
            "invoice_line_ids": invoice_line_ids
        }

    def _create_invoice_with_reconciliation(self, invoice_id=None, payments_to_reconcile=None):
        self.ensure_one()

        if invoice_id:
            # Automatic creation of invoice
            invoice = self.env["account.move"].browse(invoice_id)
        else:
            # From create invoice wizard
            invoice = self.invoice_ids[-1]

        if invoice.state == "draft":
            invoice.action_post()

        regular_payments = credit_note_payments = self.env["sale.order.payment.reconcile"]

        for reconciled_payment in self.reconciled_payment_ids:
            if reconciled_payment.credit_note_id:
                credit_note_payments += reconciled_payment
            else:
                regular_payments += reconciled_payment

        if regular_payments: 
            super(SaleOrder, self)._create_invoice_with_reconciliation(invoice_id=invoice.id, payments_to_reconcile=regular_payments)
        
        if credit_note_payments:
            for credit_note_payment in credit_note_payments.filtered(lambda p: p.payment_id.state == "valid"):
                credit_note = credit_note_payment.credit_note_id

                if credit_note.state == "draft":
                    credit_note.action_post()

                for move_line in credit_note.line_ids:
                    if move_line.account_internal_type == "receivable":
                        invoice.js_assign_outstanding_line(move_line.id)

        