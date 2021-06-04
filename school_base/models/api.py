from odoo import _
from odoo.api import Environment
from odoo.exceptions import AccessError
from odoo.tools import lazy_property


def district_code(self):
    district_code_ids = self.context.get('allowed_district_code_ids', [])
    if district_code_ids:
        if not self.su:
            user_district_code_ids = self.user.district_code_ids.ids
            if user_district_code_ids:
                if any(did not in district_code_ids for did in district_code_ids):
                    raise AccessError(_("Access to unauthorized or invalid district codes."))
            return self['school_base.district_code'].browse(district_code_ids[0])
    return self.user.district_code_id


def district_codes(self):
    district_code_ids = self.context.get('allowed_district_code_ids', [])
    if district_code_ids:
        if not self.su:
            user_district_code_ids = self.user.district_code_ids.ids
            if user_district_code_ids:
                if any(did not in district_code_ids for did in district_code_ids):
                    raise AccessError(_("Access to unauthorized or invalid district codes."))
            return self['school_base.district_code'].browse(district_code_ids)
    return self.user.district_code_id


def school_code(self):
    school_code_ids = self.context.get('allowed_school_code_ids', [])
    if school_code_ids:
        if not self.su:
            user_school_code_ids = self.user.school_code_ids.ids
            if user_school_code_ids:
                if any(did not in school_code_ids for did in school_code_ids):
                    raise AccessError(_("Access to unauthorized or invalid school codes."))
            return self['school_base.school_code'].browse(school_code_ids[0])
    return self.user.school_code_id


def school_codes(self):
    school_code_ids = self.context.get('allowed_school_code_ids', [])
    if school_code_ids:
        if not self.su:
            user_school_code_ids = self.user.school_code_ids.ids
            if user_school_code_ids:
                if any(did not in school_code_ids for did in school_code_ids):
                    raise AccessError(_("Access to unauthorized or invalid school codes."))
            return self['school_base.school_code'].browse(school_code_ids)
    return self.user.school_code_id


Environment.district_code = lazy_property(district_code)
Environment.district_codes = lazy_property(district_codes)
Environment.school_code = lazy_property(school_code)
Environment.school_codes = lazy_property(school_codes)
