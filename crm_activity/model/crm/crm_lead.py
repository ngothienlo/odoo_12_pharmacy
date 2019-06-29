# Copyright 2009-2019 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    crm_activity_history_ids = fields.One2many(
        comodel_name='activity.history',
        inverse_name='crm_lead_id',
        string='Activity History',
    )
