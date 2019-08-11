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
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    location_id = fields.Many2one(
        'stock.location', 'Delivery Location',
        domain=[('usage', '=', 'internal'), ('is_sale_location', '=', True)])
    cost_price = fields.Float(related='product_id.standard_price', store=True)
    total_cost = fields.Float(compute='_compute_total_cost', store=True)

    @api.depends('cost_price', 'product_uom_qty')
    def _compute_total_cost(self):
        for rec in self:
            cost_price = rec.cost_price or 0
            product_uom_qty = rec.product_uom_qty or 0
            rec.total_cost = cost_price * product_uom_qty

    @api.onchange('product_id')
    def _onchange_update_location(self):
        if self.product_id and\
            any(sol != self and sol.product_id ==
                self.product_id for sol in self.order_id.order_line):
            raise UserError(
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
        if not self.order_id.is_rental_order:
            product_id = self.product_id and self.product_id.id or False
            if product_id:
                so_location_id = self.env.context.get('so_location_id')
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

    @api.multi
    def _prepare_procurement_values(self, group_id=False):
        self.ensure_one()
        values = super(SaleOrderLine, self)._prepare_procurement_values(
            group_id)
        is_rental_order = self.order_id.is_rental_order
        values.update({'is_rental_order': is_rental_order})
        if not is_rental_order:
            src_location_id = False
            direct_shipping = self.order_id and\
                self.order_id.direct_shipping or False
            if direct_shipping:
                src_location_id = self.location_id and\
                    self.location_id.id or False
            else:
                src_location_id = self.order_id and\
                    self.order_id.current_location_id.id
            values.update({
                'src_location_id': src_location_id,
            })
        return values

    @api.multi
    def _create_stock_move(self):
        self.ensure_one()
        stock_move_env = self.env['stock.move']
        date_planned = fields.Datetime.now()
        move_values = {
            'location_id': self.location_id.id,
            'location_dest_id': self.order_id.current_location_id.id,
            'product_uom_qty': self.product_uom_qty,
            'product_uom': self.product_uom.id,
            'name': self.name,
            'product_id': self.product_id.id,
            'picking_type_id': self.env.ref('stock.picking_type_internal').id,
            'date': date_planned,
            'date_expected': date_planned,
            'sale_line_id': self.id
        }
        stock_move = stock_move_env.create(move_values)
        stock_move._assign_picking()
        picking = stock_move.picking_id
        if picking and not picking.sale_id:
            picking.sale_id = self.order_id.id
        return True

    @api.model
    def _prepare_value_procurement_group_run(self, procurement_group):
        vals = super(SaleOrderLine, self)._prepare_value_procurement_group_run(
            procurement_group)
        vals.update({'is_rental_order': self.order_id.is_rental_order})
        return vals
