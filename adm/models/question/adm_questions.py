# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ApplicationOptionHowHearAboutUs(models.Model):
    _name = 'adm.application.option.how.hear.about.us'
    _description = "How Questions hear about us"
    _order = 'sequence'

    name = fields.Char("Name", translate=True, required=True)
    sequence = fields.Integer(default=-1)


# Medical Options
class AdmApplicationOptionMedicalConditions(models.Model):
    _name = 'adm.application.option.medical.conditions'
    _description = "Application option medical conditions"
    _order = 'sequence'

    sequence = fields.Integer(default=-1)
    name = fields.Char(translate=True)


class AdmApplicationOptionMedicalAllergies(models.Model):
    _name = 'adm.application.option.medical.allergies'
    _description = "Application medical allergies"
    _order = 'sequence'

    sequence = fields.Integer(default=-1)
    name = fields.Char(translate=True)


class AdmApplicationOptionMedicalMedications(models.Model):
    _name = 'adm.application.option.medical.medications'
    _description = "Application medical medications"
    _order = 'sequence'

    sequence = fields.Integer(default=-1)
    name = fields.Char(translate=True)
