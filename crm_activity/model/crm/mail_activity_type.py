# Copyright 2009-2019 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class MailActivityType(models.Model):
    _inherit = "mail.activity.type"

    code = fields.Char(required=True)
    stage_id = fields.Many2one(
        comodel_name="crm.stage",
        string="Stage"
    )
    # followup_ids = fields.Many2many(
    #     comodel_name="activity.followup",
    #     string="Follow-up"
    # )
    possible_result_ids = fields.One2many(
        comodel_name="activity.type.possible.result",
        inverse_name="activity_type_id",
        string="Possible Results"
    )

    summary = fields.Text(string="Description", translate=True)

    res_model = fields.Char(
        string='Document Model Name',
        related='res_model_id.model',
        readonly=True,
        store=True
    )

    use_for_crm = fields.Boolean(
        string='Use for CRM',
        default=True
    )

    _sql_constraints = [
        ('code', 'UNIQUE (code)',
         'You can not have two activity types with the same code !')
    ]
