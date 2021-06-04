# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderPayment(models.Model):
    ######################
    # Private attributes #
    ######################
    _inherit = "sale.order.payment"

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    wallet_id = fields.Many2one(comodel_name="wallet.category", 
                                string="Related Wallet",
                                readonly=True)

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