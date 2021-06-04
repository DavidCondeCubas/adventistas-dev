# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResCompany(models.Model):
    ######################
    # Private attributes #
    ######################
    _inherit = 'res.company'

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    create_invoice_on_so_fully_paid_enabled = fields.Boolean(string="Automatic Invoice Creation", 
        help="Enable / Disable automatic invoice creation when Sales Order is Fully Paid")

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