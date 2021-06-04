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
            "invoice_payment_id": "CAST(NULL as bigint) as invoice_payment_id",
            **new_fields
        })

    def _query(self, unions=[]):
        fields = self._view_fields({
            "id": "CONCAT('I', invoice.id) as id",
            "name": "invoice.name as \"name\"",
            "payment_id": "CAST(NULL as bigint) as payment_id",
            "payment_type": "'invoice' as payment_type",
            "payment_date": "invoice.date as payment_date",
            "payment_method_id": "invoice.payment_method_id as payment_method_id",
            "pos_order_id": "CAST(NULL as bigint) as pos_order_id",
            "amount": "COALESCE(invoice.payment_amount, 0) as amount",
        })
        fields.update({
            "invoice_payment_id": "invoice.id as invoice_payment_id",
        })
        from_ = """
            pos_pr_invoice_payment invoice
                join pos_session session on (session.id=invoice.pos_session_id)
                left join account_move move on (move.id=invoice.move_id)
			        left join res_partner partner on (partner.id=move.partner_id)
        """ 
        groupby_ = """
            invoice.id,
            payment_type,
            invoice.payment_method_id,
            session.id,
            partner.id
        """
        where_ = "invoice.pos_session_id IS NOT NULL"

        query = self.generate_table_query(fields=fields, from_clause=from_, groupby=groupby_, where_clause=where_)
        return super(PosPaymentReport, self)._query(unions=[*unions, query])

    ######################
    # Fields declaration #
    ######################
    payment_type = fields.Selection(selection_add=[("invoice", "Invoice")])
    invoice_payment_id = fields.Many2one(comodel_name="pos_pr.invoice.payment",
                                         string="Invoice Payment",
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
