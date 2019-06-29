# Copyright 2009-2019 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class CrmStage(models.Model):
    _inherit = 'crm.stage'

    active = fields.Boolean(default=True)
