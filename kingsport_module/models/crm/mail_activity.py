# -*- coding: utf-8 -*-
# Copyright 2009-2019 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    @api.multi
    def mark_done_activity(self):
        lead = super(MailActivity, self).mark_done_activity()
        valid_act_type_id = self.env['mail.activity.type'].search(
            [('stage_id', '=', lead.stage_id.id)], order='sequence', limit=1)
        if valid_act_type_id:
            activity_id = self.env['mail.activity'].create({
                'activity_type_id': valid_act_type_id.id,
            })
            activity_id._onchange_activity_type_id()
            activity_id.action_close_dialog()
        return lead
