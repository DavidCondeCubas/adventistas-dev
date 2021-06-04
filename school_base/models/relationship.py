"""
Created on Feb 1, 2020

@author: LuisMora
"""
from odoo import models, fields, api, _


class SchoolBaseRelationship(models.Model):
    _name = 'school_base.relationship'
    _description = "Relationship"

    partner_individual_id = fields.Many2one(
        "res.partner", string="Individual", required=True, ondelete="cascade")
    partner_relation_id = fields.Many2one(
        "res.partner", string="Relation", required=True, ondelete="cascade")

    family_id = fields.Many2one(
        "res.partner", string="Family", required=True,
        domain=[('is_family', '=', True)], ondelete="cascade")
    relationship_type_id = fields.Many2one(
        "school_base.relationship_type", string="Relationship",
        ondelete="set null")

    custody = fields.Boolean(string="Custody")
    correspondence = fields.Boolean(string="Correspondence")
    grand_parent = fields.Boolean(string="Grand Parent")
    grade_related = fields.Boolean(string="Grade Related")
    family_portal = fields.Boolean(string="Family Portal")
    is_emergency_contact = fields.Boolean("Is an emergency contact?")

    financial_responsability = fields.Boolean()

    def write(self, vals):
        res = super(SchoolBaseRelationship, self).write(vals)
        return res


class RelationshipType(models.Model):
    """ SubStatus for students """
    _name = 'school_base.relationship_type'
    _description = "Relationship Type"
    _order = "sequence"

    name = fields.Char(string="Relationship type", required=True, translate=True)
    key = fields.Char(string="Key", translate=False)
    type = fields.Selection([
        ('daughter', _("Daughter")),
        ('son', _("Son")),
        ('child', _("Child")),

        ('sibling', _("Sibling")),
        ('brother', _("Brother")),
        ('sister', _("Sister")),

        ('parent', _("Parent")),
        ('father', _("Father")),
        ('mother', _("Mother")),

        ('grandparent', _("Grandparent")),
        ('grandmother', _("Grandmother")),
        ('grandfather', _("Grandfather")),

        ('stepparent', _("Stepparent")),
        ('stepmother', _("Stepmother")),
        ('stepfather', _("Stepfather")),
        ('stepsibling', _("Stepsibling")),
        ('stepsister', _("Stepsister")),
        ('stepbrother', _("Stepbrother")),

        ('uncle', _("Uncle")),
        ('cousin', _("Cousin")),
        ('other', _("Other")),
        ], string="Type")
    sequence = fields.Integer(default=1)
