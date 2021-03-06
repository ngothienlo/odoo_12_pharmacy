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
from dateutil.relativedelta import relativedelta


class StockMove(models.Model):
    _inherit = 'stock.move'

    warranty_expiration_date = fields.Datetime(
        compute='_compute_expiration_warranty_date')

    @api.multi
    def _compute_expiration_warranty_date(self):
        for move in self:
            if move.picking_id.state != 'done' \
                    or not move.picking_id.date_done:
                continue
            move.warranty_expiration_date = move.picking_id.date_done + \
                relativedelta(months=+move.product_id.product_tmpl_id.warranty)

    def _search_picking_for_assignation(self):
        """Overwrite for Kingsport workflow"""
        self.ensure_one()
        list_condition = self._prepare_value_for_search_picking()
        picking = self.env['stock.picking'].search(list_condition, limit=1)
        if picking:
            return picking
        return False

    @api.model
    def _prepare_value_for_search_picking(self):
        sale_order = self.sale_line_id and self.sale_line_id.order_id or False
        list_condition = [
            ('sale_id', '=', sale_order.id),
            ('group_id', '=', self.group_id.id),
            ('location_id', '=', self.location_id.id),
            ('location_dest_id', '=', self.location_dest_id.id),
            ('picking_type_id', '=', self.picking_type_id.id),
            ('printed', '=', False),
            ('state', 'in', [
                'draft', 'confirmed', 'waiting',
                'partially_available', 'assigned'])
        ]
        return list_condition

    @api.depends('product_id', 'has_tracking')
    def _compute_show_details_visible(self):
        for move in self:
            move.show_details_visible = False
