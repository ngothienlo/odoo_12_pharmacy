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
from odoo.exceptions import Warning


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    location_id = fields.Many2one('stock.location', 'Delivery Location')
    cost_price = fields.Float(related='product_id.standard_price')
    total_cost = fields.Float(compute='_compute_total_cost', store=True)

    @api.depends('cost_price', 'product_uom_qty')
    def _compute_total_cost(self):
        for rec in self:
            cost_price = rec.cost_price or 0
            product_uom_qty = rec.product_uom_qty or 0
            rec.total_cost = cost_price * product_uom_qty

    @api.onchange('product_id')
    def _onchange_update_location(self):
        if self.product_id:
            so_id = self.env.context.get('default_order_id') or False
            if so_id:
                params = [('order_id', '=', so_id),
                          ('product_id', '=', self.product_id.id), ]
                if self.id:
                    params.append(('id', '!=', self.id))
                existed_so_lines = self.env['sale.order.line'].search(params)
                if existed_so_lines:
                    raise Warning(
                        _('SO line with product %s already existed.'
                          ' Please update its quantity instead.' %
                          self.product_id.name))
            self._update_location()

    @api.onchange('product_uom_qty')
    def _onchange_product_uom_qty(self):
        if self.product_uom_qty:
            self._update_location()

    @api.model
    def _update_location(self):
        product_id = self.product_id and self.product_id.id or False
        if product_id:
            so_location_id = self.env.context.get('default_location_id')
            line_location_id = self.location_id and\
                self.location_id.id or False
            product_uom_qty = self.product_uom_qty or 0
            if line_location_id:
                self.location_id = self.check_inventory(
                    product_id, line_location_id, product_uom_qty)
            else:
                self.location_id = self.check_inventory(
                    product_id, so_location_id, product_uom_qty)
        return True

    @api.model
    def check_inventory(self, product_id, location_id, product_uom_qty):
        stock_quant_env = self.env['stock.quant']
        stock_quants = stock_quant_env.search(
            [('product_id', '=', product_id),
             ('location_id', '=', location_id)])
        is_on_hand = self.check_qty_on_hand(stock_quants, product_uom_qty)
        if is_on_hand:
            return location_id
        return False

    @api.model
    def check_qty_on_hand(self, stock_quants, product_uom_qty):
        total_on_hand = 0
        total_reserved = 0
        for stock_quant in stock_quants:
            total_on_hand += stock_quant.quantity
            total_reserved += stock_quant.reserved_quantity
        qty_to_check = total_on_hand - total_reserved
        if qty_to_check < product_uom_qty:
            return False
        return True
