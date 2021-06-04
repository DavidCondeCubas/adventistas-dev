# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.misc import formatLang


class SaleOrderPayWithWalletWizard(models.TransientModel):
    ######################
    # Private attributes #
    ######################
    _name = "sale.order.pay.with.wallet.wizard"

    ###################
    # Default methods #
    ###################
    def _default_line_ids(self):
        sale_order_id = self._context.get("active_id")
        sale_order = self.env["sale.order"].browse(sale_order_id)

        if sale_order:
            partner = sale_order.partner_id

            wallet_to_apply = sale_order._get_wallet_due_amounts()
            wallet_partner_amounts = {
                wallet_id.id: wallet_id.get_wallet_amount(partner)
                for wallet_id in self.env["wallet.category"].search([("company_id", "=", self.env.company.id)])
            }
            wallet_payment_line_ids = self.env["sale.order.pay.with.wallet.wizard.line"]

            wallet_suggestion_amounts = sale_order._calculate_wallet_distribution(
                wallet_to_apply, wallet_partner_amounts)

            for wallet_id, amount in wallet_suggestion_amounts.items():
                wallet_payment_line_id = wallet_payment_line_ids.create({
                    "partner_id": partner.id,
                    "wallet_id": wallet_id.id,
                    "amount": amount
                })
                wallet_payment_line_ids += wallet_payment_line_id
            return wallet_payment_line_ids

    ######################
    # Fields declaration #
    ######################
    partner_id = fields.Many2one(comodel_name="res.partner", required=True)
    wallet_ids = fields.Many2many(comodel_name="wallet.category",
                                  compute="_compute_wallet_ids")
    wallet_balances = fields.Html(string="Wallet Balances",
                                  compute="_compute_wallet_balances")
    used_wallet_ids = fields.Many2many(comodel_name="wallet.category",
                                       compute="_compute_used_wallet_ids")
    line_ids = fields.One2many(comodel_name="sale.order.pay.with.wallet.wizard.line",
                               inverse_name="wizard_id",
                               default=_default_line_ids)

    ##############################
    # Compute and search methods #
    ##############################
    @api.depends("partner_id")
    def _compute_wallet_ids(self):
        self.ensure_one()

        sale_order_id = self._context.get("active_id")

        if sale_order_id:
            wallet_obj = available_wallets = self.env["wallet.category"]

            sale_order = self.env["sale.order"].browse(sale_order_id)

            if sale_order:
                partner = sale_order.partner_id
                wallets = wallet_obj.search([("company_id", "=", self.env.company.id)])

                for wallet in wallets:
                    amount_total = wallet_obj.get_wallet_amount(partner, wallet)
                    
                    if amount_total > -abs(wallet.credit_limit):
                        available_wallets += wallet

                self.wallet_ids = available_wallets

    @api.depends("partner_id")
    def _compute_wallet_balances(self):
        for record in self:
            lis = ""

            if record.partner_id:
                wallet_balances = record.partner_id.get_wallet_balances_dict([])

                for wallet_id, amount in wallet_balances.items():
                    wallet = self.env["wallet.category"].browse(wallet_id)

                    lis += "<li><strong>%s:</strong> %s %s %s</li>" % (
                        wallet.name,
                        self.env.company.currency_id.symbol if self.env.company.currency_id.position == 'before' else "",
                        formatLang(self.env, amount),
                        self.env.company.currency_id.symbol if self.env.company.currency_id.position == 'after' else "")

            record.wallet_balances = "<div><ul>%s</ul></div>" % lis

    @api.depends("line_ids")
    def _compute_used_wallet_ids(self):
        for record in self:
            record.used_wallet_ids = record.line_ids.mapped("wallet_id")

    ############################
    # Constrains and onchanges #
    ############################

    #########################
    # CRUD method overrides #
    #########################

    ##################
    # Action methods #
    ##################
    def action_pay_with_wallet(self):
        self.ensure_one()

        if not self.line_ids:
            raise ValidationError("Wallet Lines should not be empty!")

        sale_order_ids = self._context.get("active_ids", [])
        sale_orders = self.env["sale.order"].browse(sale_order_ids)
        
        if sale_orders:
            wallet_payment_dict = {}
            for line in self.line_ids.filtered(lambda l: l.wallet_id.exists() and l.amount > 0):
                wallet_payment_dict[line.wallet_id.id] = line.amount

            sale_orders.pay_with_wallet(wallet_payment_dict)
            
    ####################
    # Business methods #
    ####################


class SaleOrderPayWithWalletWizardLine(models.TransientModel):
    ######################
    # Private attributes #
    ######################
    _name = "sale.order.pay.with.wallet.wizard.line"

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    wizard_id = fields.Many2one(comodel_name="sale.order.pay.with.wallet.wizard")
    partner_id = fields.Many2one(comodel_name="res.partner",
                                 required=True)
    wallet_id = fields.Many2one(comodel_name="wallet.category",
                                string="Wallet",
                                required=True)
    partner_amount = fields.Float(string="Remaining Credit",
                                  compute="_compute_partner_amount",
                                  readonly=True)
    amount = fields.Float(string="Credit to Apply")

    ##############################
    # Compute and search methods #
    ##############################
    @api.depends("wallet_id", "amount")
    def _compute_partner_amount(self):
        for line in self:
            line.partner_amount = line.wallet_id.get_wallet_amount(line.partner_id) - line.amount

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
