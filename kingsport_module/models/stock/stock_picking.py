##############################################################################
#
#    Copyright 2009-2019 Trobz (<http://trobz.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields, api, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    return_do_over_7days = fields.Boolean(copy=False)
    approver_id = fields.Many2one(
        'res.partner',
        track_visibility='onchange')
    dummy_state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('pending', 'Wait For Approval'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')],
        string='Status', compute='_compute_dummy_state',
        inverse='_update_state', store=True,
        track_visibility='onchange')
    state = fields.Selection(track_visibility='')

    @api.multi
    def _update_state(self):
        for rec in self:
            if rec.dummy_state:
                if rec.dummy_state == 'pending':
                    rec.state = 'draft'
                else:
                    rec.state = rec.dummy_state

    @api.depends('state')
    def _compute_dummy_state(self):
        for rec in self:
            if rec.state:
                rec.dummy_state = rec.state

    @api.multi
    def button_ask_for_approval(self):
        for rec in self:
            self.write({'dummy_state': 'pending'})
        return True

    @api.multi
    def approve_and_reserve(self):
        self.action_confirm()
        self.action_assign()
        partner_id = self.env.user.partner_id and\
            self.env.user.partner_id.id or False
        self.write({'approver_id': partner_id})
        return True

    @api.multi
    def button_authorized_approval(self):
        self.ensure_one()
        context = dict(self._context) or {}
        context.update({
            'default_stock_picking_id': self.id
        })
        return {
            'name': _('Authorized Approval'),
            'type': 'ir.actions.act_window',
            'res_model': 'authorized.approval',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': context
        }

    @api.multi
    @api.depends('state', 'move_lines')
    def _compute_show_mark_as_todo(self):
        super(StockPicking, self)._compute_show_mark_as_todo()
        for picking in self:
            if picking.picking_type_code == 'internal':
                picking.show_mark_as_todo = False

    @api.model
    def _update_stock_move_line(self):
        move_lines = self.move_line_ids or []
        state = ['draft', 'waiting',
                 'partially_available', 'assigned', 'confirmed']
        move_lines.filtered(lambda self: self.state in state).write({
            'location_dest_id': self.location_dest_id.id
        })
        return True

    @api.multi
    def message_track(self, tracked_fields, initial_values):
        """
        Override to update tracking values of dummy_state instead of state
        """
        if 'initial_values_dummy_state' in self._context and \
                'state' in tracked_fields.keys():
            tracked_fields.pop('state')
            tracked_fields.update(self.fields_get(['dummy_state']))
            initial_values = self._context.get('initial_values_dummy_state')
        return super(StockPicking, self).message_track(
            tracked_fields, initial_values)
