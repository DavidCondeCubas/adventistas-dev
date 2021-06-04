# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PosPaymentReport(models.Model):
    ######################
    # Private attributes #
    ######################
    _inherit = "pos.payment.report"

    ###################
    # Default methods #
    ###################
    def _view_fields(self, new_fields={}):
        return super(PosPaymentReport, self)._view_fields(new_fields={
            "wallet_load_id": "CAST(NULL as bigint) as wallet_load_id",
            **new_fields
        })

    def _query(self, unions=[]):
        fields = self._view_fields({
            "id": "CONCAT('W', load.id) as id",
            "name": "load.name as \"name\"",
            "payment_id": "CAST(NULL as bigint) as payment_id",
            "payment_type": "'wallet' as payment_type",
            "payment_date": "load.date as payment_date",
            "payment_method_id": "load.payment_method_id as payment_method_id",
            "pos_order_id": "CAST(NULL as bigint) as pos_order_id",
            "amount": "COALESCE(load.amount, 0) as amount",
        })
        fields.update({
            "wallet_load_id": "load.id as wallet_load_id",
        })
        from_ = """
            pos_wallet_wallet_load load
                join pos_session session on (session.id=load.pos_session_id)
                join res_partner partner on (partner.id=load.partner_id)
        """ 
        groupby_ = """
            load.id,
            payment_type,
            load.payment_method_id,
            session.id,
            partner.id
        """
        where_ = "load.pos_session_id IS NOT NULL"

        query = self.generate_table_query(fields=fields, from_clause=from_, groupby=groupby_, where_clause=where_)
        return super(PosPaymentReport, self)._query(unions=[*unions, query])

    ######################
    # Fields declaration #
    ######################
    payment_type = fields.Selection(selection_add=[("wallet", "Wallet")])
    wallet_load_id = fields.Many2one(comodel_name="pos_wallet.wallet.load",
                                     string="Wallet Load Payment",
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
