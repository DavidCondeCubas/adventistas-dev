# -*- coding: utf-8 -*-

from odoo import fields, models, tools, api


class AdmActivityReport(models.Model):
    """ CRM Lead Analysis """

    _name = "adm.activity.report"
    _auto = False
    _description = "ADM Activity Analysis"
    _rec_name = 'id'

    subtype_id = fields.Many2one('mail.message.subtype', 'Subtype', readonly=True)
    mail_activity_type_id = fields.Many2one('mail.activity.type', 'Activity Type', readonly=True)
    author_id = fields.Many2one('res.partner', 'Assigned To', readonly=True)
    date = fields.Datetime('Completion Date', readonly=True)
    body = fields.Html('Activity Description', readonly=True)

    application_id = fields.Many2one('adm.application', "Application", readonly=True)
    status_id = fields.Many2one('adm.application.status', "Status", readonly=True)
    # company_id = fields.Many2one('adm.application.status', "Status", readonly=True)
    # lead_type = fields.Selection(
    #     string='Type',
    #     selection=[('lead', 'Lead'), ('opportunity', 'Opportunity')],
    #     help="Type is used to separate Leads and Opportunities")
    # active = fields.Boolean('Active', readonly=True)

    def _select(self):
        return """
            SELECT
                m.id,
                m.subtype_id,
                m.mail_activity_type_id,
                m.author_id,
                m.date,
                m.body,
                
                a.id as application_id,
                a.status_id
        """

    def _from(self):
        return """
            FROM mail_message AS m
        """

    def _join(self):
        return """
            JOIN adm_application AS a ON m.res_id = a.id
        """


    def _where(self):
        disccusion_subtype = self.env.ref('mail.mt_comment')
        return """
            WHERE
                m.model = 'adm.application' AND (m.mail_activity_type_id IS NOT NULL OR m.subtype_id = %s)
        """ % (disccusion_subtype.id,)

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                %s
                %s
                %s
                %s
            )
        """ % (self._table, self._select(), self._from(), self._join(), self._where())
        )
