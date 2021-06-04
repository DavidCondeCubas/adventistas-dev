"""
Created on Feb 18, 2020

@author: LuisMora
"""
from odoo import models, fields


class SchoolBaseMedicalMedication(models.Model):
    _name = 'school_base.medical_medication'
    _description = "Medical medication"

    name = fields.Char("Name")
    comment = fields.Char("Comment")
    
    partner_id = fields.Many2one("res.partner", string="Partner")