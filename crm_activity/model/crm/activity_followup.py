# Copyright 2009-2019 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ActivityFollowup(models.Model):
    _name = 'activity.followup'
    _description = 'Activity Followup'
    _order = 'sequence'

    name = fields.Char(string='Name', required=True)
    sequence = fields.Char(string='Sequence')
    hours_to_followup = fields.Float(string='Hours to Follow-up')
