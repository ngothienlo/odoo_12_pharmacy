# -*- coding: utf-8 -*-
# Copyright 2009-2019 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import clean_context


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    activity_result_id = fields.Many2one(
        comodel_name='activity.result',
        string='Result'
    )
    state = fields.Selection(selection_add=[('done', 'done')], store=True)

    activity_type_result_ids = fields.Many2many(
        comodel_name='activity.result',
        compute='_compute_activity_type_result_ids',
        store=False
        # store = False to avoid change value on model mail.activity
        # that will raise access rule (mail.activity: user: own only)
    )

    # Help to domain activity type by crm_lead stage
    domain_activity_type_ids = fields.Many2many(
        comodel_name="mail.activity.type",
        compute="_compute_domain_activity_type_ids",
        store=False,
        # store = False to avoid change value on model mail.activity
        # that will raise access rule (mail.activity: user: own only)
    )
    followup_id = fields.Many2one(
        comodel_name="activity.followup"
    )

    @api.depends('activity_type_id', 'activity_type_id.possible_result_ids')
    def _compute_activity_type_result_ids(self):
        for activity in self:
            activity_type = activity.activity_type_id
            activity.activity_type_result_ids = \
                activity_type.possible_result_ids.mapped('result_id')

    @api.depends('res_model_id', 'res_id')
    def _compute_domain_activity_type_ids(self):
        for activity in self:
            res_model_id = activity.res_model_id
            res_model_name = activity.res_model
            res_id = activity.res_id
            domain = [
                "|",
                ('res_model_id', '=', False),
                ('res_model_id', '=', res_model_id.id),
            ]
            res_model_domain = []
            if res_model_name == 'crm.lead' and res_id:
                active_lead = self.env[res_model_name].browse(res_id)
                res_model_domain = [
                    ('stage_id', '=', active_lead.stage_id.id)
                ]
            combined_domain = res_model_domain + domain
            activity.domain_activity_type_ids = \
                self.env["mail.activity.type"].search(combined_domain)

    @api.multi
    def create_history_activity(self):
        for record in self:
            if record.res_model == 'crm.lead':
                ctx = dict(self._context) or {}
                if ctx.get('default_res_id' or False):
                    crm_lead_obj = self.env['crm.lead'].browse(
                        ctx['default_res_id']
                    )
                    mail_activity_ids = \
                        crm_lead_obj.crm_activity_history_ids.mapped(
                            'mail_activity_id')
                    vals_history = {
                        'activity_type_id': record.activity_type_id.id,
                        'summary': record.summary,
                        'date_deadline': record.date_deadline,
                        'user_id': record.user_id.id,
                        'activity_result_id': record.activity_result_id.id,
                        'mail_activity_id': record.id,
                        'followup_id':
                            record.followup_id and record.followup_id.id or
                            False,
                        'note': record.note,
                        'status': ctx.get('is_done', record.state),
                    }
                    if record.id not in mail_activity_ids.ids:
                        vals = {
                            'crm_activity_history_ids': [
                                (0, 0, vals_history)
                            ]
                        }
                    else:
                        rec = crm_lead_obj.crm_activity_history_ids.filtered(
                            lambda r: r.mail_activity_id.id == record.id
                        )
                        vals = {
                            'crm_activity_history_ids': [
                                (1, rec.id, vals_history)
                            ]
                        }
                    crm_lead_obj.write(vals)
        return True

    @api.multi
    def action_close_dialog(self):
        self.create_history_activity()
        return super(MailActivity, self).action_close_dialog()

    def action_done_schedule_next(self):
        ctx = dict(self._context) or {}
        ctx.update({'is_done': 'done'})
        self.with_context(ctx).create_history_activity()
        return super(MailActivity, self).action_feedback_schedule_next()

    @api.multi
    def action_done(self):
        self.ensure_one()
        ctx = self._context.copy()
        ctx.update({'is_done': 'done'})
        self.mark_done_activity_with_followup()
        self.with_context(ctx).create_history_activity()
        super(MailActivity, self).action_done()

    def action_feedback(self, feedback=False):
        self = self.with_context(action_feedback=True)
        return super(MailActivity, self).action_feedback(feedback)

    @api.multi
    def mark_done_activity_with_followup(self):
        self.ensure_one()
        if self.res_model != 'crm.lead':
            return

        activity_result = self.activity_result_id
        if not activity_result:
            raise UserError(_("Missing result of activity to make it done."))

        activity_type = self.activity_type_id
        activity_type_followups = activity_type.followup_ids
        is_followup_result = activity_result.follow_up

        current_lead = self.env['crm.lead'].browse(self.res_id)
        activity_history_ids = current_lead.crm_activity_history_ids.filtered(
            lambda act_ht: act_ht.followup_id in activity_type_followups and
            act_ht.activity_type_id == self.activity_type_id
        )
        ctx = dict(
            clean_context(self.env.context),
            default_previous_activity_type_id=self.activity_type_id.id,
            default_res_id=self.res_id,
            default_res_model=self.res_model,
            activity_previous_deadline=self.date_deadline,
        )
        previous_deadline = fields.Date.from_string(self.date_deadline)
        possible_activity_type_result = \
            activity_type.possible_result_ids.filtered(
                lambda ps: ps.result_id == activity_result
            )
        possible_activity_type_result = possible_activity_type_result and \
            possible_activity_type_result[0] or False
        next_stage = destination_stage = possible_activity_type_result \
            and possible_activity_type_result.destination_stage_id or False

        if activity_type_followups and is_followup_result:
            if len(activity_history_ids) < len(activity_type_followups):
                # Update stage for lead
                if destination_stage \
                        and destination_stage != current_lead.stage_id:
                    current_lead.stage_id = destination_stage

                previous_followups = activity_history_ids.mapped(
                    'followup_id')
                un_used_followups = [
                    flu
                    for flu in activity_type_followups
                    if flu not in previous_followups
                ]
                followup = un_used_followups and un_used_followups[0] or False
                new_deadline = previous_deadline + relativedelta(
                    **{'hours': followup.hours_to_followup}
                )
                ctx.update(dict(
                    default_date_deadline=fields.Date.to_string(new_deadline),
                    default_followup_id=followup.id,
                    default_activity_type_id=self.activity_type_id.id,
                    default_summary=self.activity_type_id.summary,
                ))
                # Create new followup activity
                Activity = self.env['mail.activity'].with_context(ctx)
                res = Activity.new(Activity.default_get(Activity.fields_get()))
                Activity.create(res._convert_to_write(res._cache))
                return True
            else:
                # Update next stage when reached the last follow up
                next_stage = possible_activity_type_result \
                    and possible_activity_type_result.final_stage_id or False

        #  Update next_state and create new activity
        if not next_stage:
            next_stage = self.env['crm.stage'].search([
                ('sequence', '>=', current_lead.stage_id.sequence)
            ], order="sequence", limit=1)
            if not next_stage:
                return
        if current_lead.stage_id != next_stage:
            current_lead.stage_id = next_stage

        next_activity_type = self.env['mail.activity.type'].search([
            ('stage_id', '=', next_stage.id)
        ], order="sequence", limit=1)
        if not next_activity_type:
            return
        ctx.update(dict(
            activity_previous_deadline=previous_deadline,
            default_activity_type_id=next_activity_type.id,
        ))
        Activity = self.env['mail.activity'].with_context(ctx)
        res = Activity.new(Activity.default_get(Activity.fields_get()))
        res._onchange_activity_type_id()
        Activity.create(res._convert_to_write(res._cache))
        return True

    @api.multi
    def unlink(self):
        self.update_history_status()
        return super(MailActivity, self).unlink()

    @api.multi
    def update_history_status(self):
        # Update Activity history status to cancel when an activity has
        # been canceled
        # When an activity done it will be unlink in action_feedback, so we
        # will avoid this case by context action_feedback
        ctx = dict(self._context) or {}
        if not ctx.get('action_feedback', False):
            for activity in self:
                history = activity.env['activity.history'].search([(
                    'mail_activity_id', '=', activity.id)])
                if history:
                    history.write({
                        'status': 'cancel',
                    })
