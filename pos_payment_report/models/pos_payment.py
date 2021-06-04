# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PosPayment(models.Model):
    ######################
    # Private attributes #
    ######################
    _inherit = "pos.payment"

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
    def name_get(self):
        # Had to do this because it displays the amount by default
        res = []
        for record in self:
            res.append((record.id, "%s/%s" % (record.session_id.name, record.id)))
        return res

    ##################
    # Action methods #
    ##################

    ####################
    # Business methods #
    ####################