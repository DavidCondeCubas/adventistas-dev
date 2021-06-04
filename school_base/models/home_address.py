# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SchoolBaseHomeAddress(models.Model):
    _name = 'school_base.home_address'
    _description = "Home address"

    name = fields.Char("Name", compute='_compute_name', store=True)
    country_id = fields.Many2one("res.country", string="Country", required=True)
    state_id = fields.Many2one("res.country.state", string="State")

    city = fields.Char("City")
    zip = fields.Char("Zip")
    street = fields.Char("Street")
    street2 = fields.Char("Street2")
    phone = fields.Char("Homephone")
    facts_id = fields.Integer("Facts ID")

    family_id = fields.Many2one("res.partner", string="Family",
                                domain="[('is_company', '=', True, ('is_family', '=', True))]")

    @api.constrains("facts_id")
    def _check_facts_id(self):
        for home_address_id in self:
            if home_address_id.facts_id:
                should_be_unique = self.search_count(
                    [("facts_id", "=", home_address_id.facts_id)])
                if should_be_unique > 1:
                    raise ValidationError("Another Home Address has the same facts id! (%s)" % home_address_id.facts_id)

    @api.onchange('country_id')
    def onchange_country_id(self):
        """ Just reset all from state """
        reset_fields = ['state_id', 'city', 'zip', 'street', 'street2', 'phone']
        self.write({field: False for field in reset_fields})

    @api.onchange('state_id')
    def onchange_state_id(self):
        """ Just reset all from city """
        reset_fields = ['city', 'zip', 'street', 'street2', 'phone']
        self.write({field: False for field in reset_fields})

    @api.model
    def _address_fields(self):
        """ Returns the list of address fields that are synced from the parent. """
        ADDRESS_FIELDS = ('street', 'street2', 'zip', 'city', 'state_id', 'country_id')
        return list(ADDRESS_FIELDS)

    @api.model
    def _formatting_address_fields(self):
        """Returns the list of address fields usable to format addresses."""
        return self._address_fields()

    def _display_address_depends(self):
        # field dependencies of method _display_address()
        return self._formatting_address_fields() + [
            'country_id.address_format', 'country_id.code', 'country_id.name', 'state_id.code', 'state_id.name',
        ]

    @api.model
    def _get_default_address_format(self):
        return "%(street)s\n%(street2)s\n%(city)s %(state_code)s %(zip)s\n%(country_name)s"

    @api.model
    def _get_address_format(self):
        return self.country_id.address_format or self._get_default_address_format()

    def _display_address(self):
        # Just taken from res.partner _display_address
        address_format = self._get_address_format()
        args = {
            'state_code': self.state_id.code or '',
            'state_name': self.state_id.name or '',
            'country_code': self.country_id.code or '',
            'country_name': self.country_id.name or '',
            'company_name': '',
        }
        for field in self._formatting_address_fields():
            args[field] = getattr(self, field) or ''
        return address_format % args

    @api.depends(lambda self: self._display_address_depends())
    def _compute_name(self):
        for home_address in self:
            # address_format = home_address.country_id.address_format
            home_address.name = home_address._display_address()
