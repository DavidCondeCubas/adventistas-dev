# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    amount_30_days = fields.Monetary(string="1-30 days",
        compute="_compute_days_amount")
    amount_60_days = fields.Monetary(string="31-60 days",
        compute="_compute_days_amount")
    amount_90_days = fields.Monetary(string="61-90 days",
        compute="_compute_days_amount")
    amount_120_days = fields.Monetary(string="91-120 days",
        compute="_compute_days_amount")
    amount_above_120_days = fields.Monetary(string="more than 120 days",
        compute="_compute_days_amount")
    computed_invoice_date_due = fields.Datetime(string="Computed Due Date",
        compute="_compute_computed_invoice_date_due",
        store=True)
    invoice_payment_state = fields.Selection(string="Invoice Payment Status",
        selection=[
            ("no", "No Invoice"),
            ("draft", "Draft Invoice"),
            ("unpaid", "Unpaid Invoice"),
            ("paid", "Paid Invoice")],
        compute="_compute_invoice_payment_state",
        store=True)
    remaining_amount = fields.Monetary(string="Remaining Amount",
        compute="_compute_remaining_amount",
        store=True)

    @api.depends("invoice_ids", "invoice_ids.state", "invoice_ids.amount_residual", "invoice_ids.invoice_payment_state")
    def _compute_invoice_payment_state(self):
        for order in self:
            invoices = order.invoice_ids.filtered(lambda x: x.type in ["out_invoice", "out_receipt"] and x.state != "cancel")
            result = "no"
            if invoices.filtered(lambda x: x.state == "draft"):
                result = "draft"
            elif invoices.filtered(lambda x: x.invoice_payment_state not in ["paid"]):
                result = "unpaid"
            elif invoices.filtered(lambda x: x.invoice_payment_state in ["paid"]):
                result = "paid"
            order.invoice_payment_state = result

    @api.depends("date_order", "invoice_date_due", "payment_term_id")
    def _compute_computed_invoice_date_due(self):
        for order in self:
            date_due = order.date_order
            if order.invoice_date_due:
                date_due = order.invoice_date_due
            elif order.payment_term_id:
                date_order = fields.Date.from_string(order.date_order)
                date_due = order.payment_term_id.compute(1, date_ref=date_order, currency=order.currency_id)[0][0]
                date_due = fields.Date.from_string(date_due)
                diff = (date_due - date_order).days
                date_due = order.date_order + relativedelta(days=diff)
            order.computed_invoice_date_due = date_due
    
    @api.depends("invoice_ids", "invoice_ids.state", "invoice_ids.amount_total")
    def _compute_remaining_amount(self):
        for so in self:
            invoices = so.invoice_ids.filtered(lambda x: x.type in ["out_invoice", "out_receipt"] and x.state != "cancel")
            remaining_amount = so.amount_total - sum(invoices.mapped("amount_total"))
            if remaining_amount < 0:
                remaining_amount = 0
            so.remaining_amount = remaining_amount

    def _compute_days_amount(self):
        for order in self:
            result_30_days = 0.0
            result_60_days = 0.0
            result_90_days = 0.0
            result_120_days = 0.0
            result_above_120_days = 0.0
            if order.computed_invoice_date_due:
                diff = fields.Datetime.now() - order.computed_invoice_date_due
                if diff.days > 120:
                    result_above_120_days = order.remaining_amount
                elif diff.days > 90:
                    result_120_days = order.remaining_amount
                elif diff.days > 60:
                    result_90_days = order.remaining_amount
                elif diff.days > 30:
                    result_60_days = order.remaining_amount
                elif diff.days >= 1:
                    result_30_days = order.remaining_amount
            order.amount_30_days = result_30_days
            order.amount_60_days = result_60_days
            order.amount_90_days = result_90_days
            order.amount_120_days = result_120_days
            order.amount_above_120_days = result_above_120_days