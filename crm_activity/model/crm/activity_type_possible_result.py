# Copyright 2009-2019 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ActivityTypePossibleResult(models.Model):
    _name = "activity.type.possible.result"
    _description = "Activity Type Possible Result"
    _rec_name = 'result_id'

    result_id = fields.Many2one(
        comodel_name="activity.result",
        string="Name",
        required=True
    )
    destination_stage_id = fields.Many2one(
        comodel_name="crm.stage",
        required=True,
        string="Destination Stage"
    )
    final_stage_id = fields.Many2one(
        comodel_name="crm.stage",
        string="Stage after Final Follow-up"
    )
    activity_type_id = fields.Many2one(
        comodel_name="mail.activity.type",
        string="Activity Type"
    )
    is_result_followup = fields.Boolean(related="result_id.follow_up")
