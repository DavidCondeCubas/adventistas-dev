# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PosSession(models.Model):
    ######################
    # Private attributes #
    ######################
    _inherit = "pos.session"

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    consolidated_payments_amount = fields.Float(compute="_compute_consolidated_payments_amount")

    ##############################
    # Compute and search methods #
    ##############################
    @api.depends("total_payments_amount")
    def _compute_consolidated_payments_amount(self):
        for record in self:
            record.consolidated_payments_amount = record.total_payments_amount

    ############################
    # Constrains and onchanges #
    ############################

    #########################
    # CRUD method overrides #
    #########################

    ##################
    # Action methods #
    ##################
    def action_show_consolidated_payments_list(self):
        self.ensure_one()
        return {
            "name": "Payments",
            "type": "ir.actions.act_window",
            "res_model": "pos.payment.report",
            "view_mode": "tree,pivot,graph",
            "domain": [("session_id", "=", self.id)],
            "context": {
                "search_default_group_by_payment_type": 1
            }
        }

    ####################
    # Business methods #
    ####################