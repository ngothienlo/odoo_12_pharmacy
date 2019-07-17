# Copyright 2009-2019 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ActivityHistory(models.Model):
    _name = 'activity.history'
    _description = 'Activity History'

    activity_type_id = fields.Many2one(
        'mail.activity.type', 'Activity',
    )
    summary = fields.Char(
        'Summary',
    )
    date_deadline = fields.Date(
        'Due Date',
        index=True,
        required=True,
        default=fields.Date.context_today,
    )
    user_id = fields.Many2one(
        'res.users', 'Assigned to',
        default=lambda self: self.env.user,
        index=True, required=True,
    )
    activity_result_id = fields.Many2one(
        comodel_name='activity.result',
        string='Result',
    )
    status = fields.Selection(
        string='Status',
        selection=[
            ('planned', 'Planned'),
            ('today', 'Today'),
            ('overdue', 'Overdue'),
            ('done', 'Done'),
            ('cancel', 'Cancel'),
        ],
        default='today',
    )
    note = fields.Html('Feedback',)
    mail_activity_id = fields.Many2one(
        comodel_name='mail.activity',
        string='Mail Activity',
    )
    crm_lead_id = fields.Many2one(
        comodel_name='crm.lead',
        string='CRM Lead',
    )
    # followup_id = fields.Many2one(
    #     comodel_name="activity.followup"
    # )
