# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    ######################
    # Private attributes #
    ######################
    _inherit = "account.move"

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    sale_order_payment_reconcile_id = fields.One2many(comodel_name="sale.order.payment.reconcile",
                                                      inverse_name="credit_note_id")

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

    ####################
    # Business methods #
    ####################