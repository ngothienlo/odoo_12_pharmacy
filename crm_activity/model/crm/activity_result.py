# Copyright 2009-2019 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models, fields


class ActivityResult(models.Model):
    _name = 'activity.result'
    _description = 'Activity Result'

    name = fields.Char(
        string='Name',
        required=True,
    )
    code = fields.Char(
        string='Code',
    )
    # follow_up = fields.Boolean(string="Follow-up ?", )
