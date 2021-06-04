# -*- coding: utf-8 -*-

from collections import OrderedDict

from odoo import tools
from odoo import models, fields, api


class PosPaymentReport(models.Model):
    ######################
    # Private attributes #
    ######################
    _name = "pos.payment.report"
    _description = "Point of Sale Payments Report"
    _auto = False
    _rec_name = "payment_date"
    _order = "payment_date desc"

    ###################
    # Default methods #
    ###################
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (
            self._table, self._query()))

    def _with(self, with_clause=""):
        return ("WITH %s" % with_clause) if with_clause else ""

    def _view_fields(self, new_fields={}):
        """Common fields"""
        
        return OrderedDict(**{
            "id": "CONCAT('P', payment.id) as id",
            "name": "payment.name as \"name\"",
            "session_id": "session.id as session_id",
            "payment_id": "payment.id as payment_id",
            "payment_type": "'regular' as payment_type",
            "partner_id": "partner.id as partner_id",
            "payment_date": "payment.payment_date as payment_date",
            "payment_method_id": "payment.payment_method_id as payment_method_id",
            "pos_order_id": "porder.id as pos_order_id",
            "amount": "sum(payment.amount / CASE COALESCE(porder.currency_rate, 0) WHEN 0 THEN 1.0 ELSE porder.currency_rate END) as amount",
            **new_fields
        })

    def _from(self, from_clause=""):
        return """
            pos_payment payment
                join pos_session session on (session.id=payment.session_id)
                join pos_order porder on (payment.pos_order_id=porder.id)
			        join res_partner partner on (porder.partner_id=partner.id)
                %s 
        """ % from_clause

    def _groupby(self, groupby=""):
        return """
            payment.id,
            payment_type,
            payment.payment_method_id,
            porder.id,
            session.id,
            partner.id %s
        """ % (groupby)

    def _query(self, unions=[]):
        with_ = self._with()
        fields = self._view_fields()
        from_ = self._from()
        groupby_ = self._groupby()
        where_ = "payment.pos_order_id IS NOT NULL"

        query = self.generate_table_query(with_clause=with_, fields=fields, from_clause=from_, groupby=groupby_, where_clause=where_)
        unioned = " UNION ".join([query, *unions])
        return unioned
    
    ######################
    # Fields declaration #
    ######################
    name = fields.Char(string="Name", readonly=True)
    session_id = fields.Many2one(comodel_name="pos.session",
                                 string="Session",
                                 readonly=True)
    payment_id = fields.Many2one(comodel_name="pos.payment",
                                 string="Payment",
                                 readonly=True)
    payment_type = fields.Selection(string="Type",
                                    selection=[("regular", "Regular Payment")],
                                    default="regular",
                                    readonly=True)
    partner_id = fields.Many2one(comodel_name="res.partner",
                                 string="Partner",
                                 readonly=True)
    payment_date = fields.Datetime(string="Date",
                                   readonly=True)
    payment_method_id = fields.Many2one(comodel_name="pos.payment.method",
                                        string="Payment Method",
                                        readonly=True)
    pos_order_id = fields.Many2one(comodel_name="pos.order",
                               string="Order",
                               readonly=True)
    amount = fields.Float("Amount", readonly=True)

    ##############################
    # Compute and search methods #
    ##############################

    ############################
    # Constrains and onchanges #
    ############################

    #########################
    # CRUD method overrides #
    #########################
    @api.model
    def generate_table_query(self, with_clause="", fields={}, groupby="", from_clause="", where_clause=""):
        with_ = ("WITH %s" % with_clause) if with_clause else ""
        where_ = ("WHERE %s" % where_clause) if where_clause else ""

        select_ = ", ".join(fields.values())

        return "%s (SELECT %s FROM %s %s IS NOT NULL GROUP BY %s)" % (with_, select_, from_clause, where_, groupby)


    ##################
    # Action methods #
    ##################

    ####################
    # Business methods #
    ####################
