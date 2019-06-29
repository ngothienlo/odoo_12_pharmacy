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


class SaleModelSelection(models.TransientModel):
    _name = 'sale.location.selection'
    _description = 'Sale Location Selection'

    stock_quant_id = fields.Many2one('stock.quant', 'Stock Quant')
    product_id = fields.Many2one(
        'product.product', related='stock_quant_id.product_id', store=True)
    location_id = fields.Many2one(
        'stock.location', related='stock_quant_id.location_id', store=True)
    quantity = fields.Float(related='stock_quant_id.quantity', store=True)
    reserved_quantity = fields.Float(
        related='stock_quant_id.reserved_quantity', store=True)
    selected_location = fields.Boolean()

    @api.multi
    def action_cancel_choose_stock_quants(self):
        self.ensure_one()
        context = dict(self._context) or {}
        sale_order_id = context.get('current_sale_order', False)

        # Reset location_id of related SO lines
        so_lines = self.env['sale.order.line'].search(
            [('order_id', '=', sale_order_id),
             ('product_id', '=', self.product_id.id)])
        so_lines.update({'location_id': False})
        self.selected_location = False
        return True

    @api.multi
    def action_choose_stock_quants(self):
        self.ensure_one()
        context = dict(self._context) or {}
        sale_order_id = context.get('current_sale_order', False)

        # Reset selected stock quant before selecting the new one
        sale_location_selections = self.env['sale.location.selection'].search(
            [('product_id', '=', self.product_id.id)])
        sale_location_selections.update({'selected_location': False})
        self.selected_location = True

        # Updating location_id of related SO lines
        so_lines = self.env['sale.order.line'].search(
            [('order_id.id', '=', sale_order_id),
             ('product_id', '=', self.product_id.id)])
        so_lines.update({'location_id': self.location_id})
        return True
