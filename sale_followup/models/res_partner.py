# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_total_due = fields.Monetary("Total Unpaid Sales",
        compute="_compute_for_sale_followup")
    sale_total_overdue = fields.Monetary("Total Overdue Sales",
        compute="_compute_for_sale_followup")
    unpaid_sale_ids = fields.One2many(string="Unpaid Sales",
        comodel_name="sale.order",
        compute="_compute_for_sale_followup")
    
    def _compute_for_sale_followup(self):
        sale_obj = self.env["sale.order"]
        for partner in self:
            unpaid_sales = sale_obj.search([
                ("state","in",["sale","done"]),
                ("invoice_payment_state","!=","paid"),
                ("partner_id","=",partner.id)
            ])
            partner.unpaid_sale_ids = unpaid_sales
            partner.sale_total_due = sum(unpaid_sales.mapped("amount_total"))
            partner.sale_total_overdue = sum(unpaid_sales.filtered(lambda x: x.computed_invoice_date_due <= datetime.now()).mapped("amount_total"))

    def action_open_sale_followup(self):
        self.ensure_one()
        return {
            "name": "Unpaid Sales for %s" % self.name,
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "views": [[self.env.ref("sale_followup.res_partner_view_form_followup").id, "form"]],
            "res_model": "res.partner",
            "res_id": self.id,
            "context": {"edit": 0, "create": 0, "delete": 0}
        }