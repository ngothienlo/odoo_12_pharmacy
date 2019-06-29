# Copyright 2009-2019 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models, fields

ODOO_NATIVE_FIELDS = (
    "'id'",
    "'create_date'",
    "'create_uid'",
    "'write_date'",
    "'write_uid'",)


class CrmStage(models.Model):
    _inherit = 'crm.stage'

    mandatory_fields = fields.Many2many(
        'ir.model.fields',
        string="Mandatory Fields",
        domain="["
        "('model', '=', 'crm.lead'),"
        "('store', '=', True),"
        "('name', 'not in', [%s])]" % ','.join(ODOO_NATIVE_FIELDS))
