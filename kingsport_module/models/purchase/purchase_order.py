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
from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _default_location_dest(self):
        pt = self.picking_type_id or False
        if pt:
            pt_code = pt.code or ''
            if pt_code == 'incoming':
                stock_location = pt.default_location_dest_id or False
                if stock_location and stock_location.allow_to_receive_good:
                    return stock_location.id
        return False

    @api.depends('picking_ids', 'picking_ids.state')
    def _compute_related_receipts(self):
        for rec in self:
            is_adjust_after_validation = True
            for picking in rec.picking_ids:
                pk_state = picking.state or ''
                if pk_state == 'done':
                    is_adjust_after_validation = False
                    break
            rec.adjust_after_validation = is_adjust_after_validation

    location_dest_id = fields.Many2one(
        'stock.location', 'Location Destination',
        domain=[('allow_to_receive_good', '=', True)],
        default=lambda self: self._default_location_dest(),
        required=True, track_visibility='onchange')
    contract_number = fields.Char()
    contract_date = fields.Date()
    date_planned = fields.Datetime(
        required=True, readonly=False, copy=True,
        track_visibility='onchange')
    adjust_after_validation = fields.Boolean(
        compute='_compute_related_receipts', store=True)
    picking_type_id = fields.Many2one(readonly=False)

    @api.onchange("picking_type_id")
    def _update_default_location_dest(self):
        self.location_dest_id = self._default_location_dest() or False

    @api.multi
    def update_stock_picking(self):
        for rec in self:
            pickings = rec.picking_ids or []
            location_dest_id = rec.location_dest_id and\
                rec.location_dest_id.id or False
            scheduled_date = rec.date_planned or False
            for picking in pickings:
                pk_state = picking.state or ''
                if pk_state != 'cancel':
                    picking.write({
                        'location_dest_id': location_dest_id,
                        'scheduled_date': scheduled_date
                    })
        return True

    @api.multi
    def write(self, vals):
        res = super(PurchaseOrder, self).write(vals)
        date_planned = vals.get('date_planned', False)
        location_dest_id = vals.get('location_dest_id', False)
        if date_planned or location_dest_id:
            self.update_stock_picking()
        return res

    @api.onchange("picking_type_id")
    def _update_default_location_dest(self):
        self.location_dest_id = self._default_location_dest() or False

    @api.model
    def _prepare_picking(self):
        res = super(PurchaseOrder, self)._prepare_picking()
        if self.location_dest_id:
            res.update({
                'location_dest_id': self.location_dest_id.id
            })
        return res

    @api.multi
    def _get_destination_location(self):
        self.ensure_one()
        if self.location_dest_id:
            return self.location_dest_id.id
        return super(PurchaseOrder, self)._get_destination_location()
