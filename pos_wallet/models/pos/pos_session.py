# -*- coding: utf-8 -*-
from collections import defaultdict

from odoo import fields, models, api, _, exceptions


class PosSession(models.Model):
    _inherit = "pos.session"

    pos_wallet_load_ids = fields.One2many('pos_wallet.wallet.load', 'pos_session_id')
    # pos_wallet_payment_ids = fields.One2many('pos_wallet.wallet.payment', 'pos_session_id')

    pos_wallet_loads_amount = fields.Float(compute='_compute_cash_balance', store=True)

    def _validate_session(self):
        action = super()._validate_session()

        if self.pos_wallet_load_ids:
            self.pos_wallet_load_ids.filtered(lambda load: not load.reconciled).apply_loads()
            self.pos_wallet_load_ids.mapped('partner_id')._compute_json_dict_wallet_amounts()

        return action

    @api.depends('payment_method_ids', 'order_ids', 'cash_register_balance_start', 'cash_register_id', 'pos_wallet_load_ids')
    def _compute_cash_balance(self):
        super()._compute_cash_balance()
        for session in self:
            session.pos_wallet_loads_amount = sum(session.pos_wallet_load_ids.mapped('amount'))
            wallet_cash_amount = 0.0 if session.state == 'closed' else sum(session.pos_wallet_load_ids.filtered('payment_method_id.is_cash_count').mapped('amount'))
            session.cash_register_total_entry_encoding += wallet_cash_amount
            session.cash_register_balance_end += wallet_cash_amount
            session.cash_register_difference -= wallet_cash_amount

    def _create_cash_statement_lines_and_cash_move_lines(self, data):
        data = super(PosSession, self)._create_cash_statement_lines_and_cash_move_lines(data)

        statements_by_journal_id = {statement.journal_id.id: statement for statement in self.statement_ids}
        load_ids = self.pos_wallet_load_ids.filtered(lambda load: not load.reconciled)
        split_cash_statement_lines = data['split_cash_statement_lines']
        combine_cash_statement_lines = data['combine_cash_statement_lines']

        payment_method_amounts = load_ids._get_payment_method_amounts(cash=True)
        for payment_method_id, amount in payment_method_amounts.items():

            statement = statements_by_journal_id[payment_method_id.cash_journal_id.id]

            statement_line_values = self._get_statement_line_vals(statement, payment_method_id.receivable_account_id, amount)
            BankStatementLine = self.env['account.bank.statement.line']
            statement_line = BankStatementLine.create(statement_line_values)
            combine_cash_statement_lines[statement] += statement_line

        # for payment, amounts in payment_method_amounts.items():
        #
        #     statement = statements_by_journal_id[
        #         payment.payment_method_id.cash_journal_id.id]
        #     split_cash_statement_line_vals[statement].append(
        #         self._get_statement_line_vals(statement,
        #                                       payment.payment_method_id.receivable_account_id,
        #                                       amounts['amount'],
        #                                       payment.payment_date))
        #     split_cash_receivable_vals[statement].append(
        #         self._get_split_receivable_vals(payment, amounts['amount'],
        #                                         amounts['amount_converted']))
        # handle combine cash payments
        # combine_cash_statement_line_vals = defaultdict(list)
        # combine_cash_receivable_vals = defaultdict(list)
        # for payment_method, amounts in combine_receivables_cash.items():
        #     if not float_is_zero(amounts['amount'],
        #                          precision_rounding=self.currency_id.rounding):
        #         statement = statements_by_journal_id[
        #             payment_method.cash_journal_id.id]
        #         combine_cash_statement_line_vals[statement].append(
        #             self._get_statement_line_vals(statement,
        #                                           payment_method.receivable_account_id,
        #                                           amounts['amount']))
        #         combine_cash_receivable_vals[statement].append(
        #             self._get_combine_receivable_vals(payment_method,
        #                                               amounts['amount'],
        #                                               amounts[
        #                                                   'amount_converted']))

        return data

    @api.model
    def get_partner_receivable(self, partner_id):
        return self.env['res.partner'].browse(partner_id).property_account_receivable_id

