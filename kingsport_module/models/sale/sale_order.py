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


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    approval_id = fields.Many2one(
        'res.partner', 'Approver',
        domain=[('customer', '=', False), ('supplier', '=', False)])
    direct_shipping = fields.Boolean()
    location_id = fields.Many2one(
        'stock.location', 'Delivery Location',
        domain=[('usage', '=', 'internal')])
    maintenance_order = fields.Boolean()
    delivery_order = fields.Many2one('stock.picking')
    exchange_order = fields.Boolean()
    original_order = fields.Many2one('sale.order')
    total_cost_price = fields.Char(
        compute='_compute_total_cost_price', store=True)

    @api.depends('order_line.total_cost')
    def _compute_total_cost_price(self):
        for rec in self:
            sale_order_lines = rec.order_line or False
            if sale_order_lines:
                total_cost_price = 0
                for sale_order_line in sale_order_lines:
                    total_cost = sale_order_line.total_cost or 0
                    total_cost_price += total_cost
                rec.total_cost_price = total_cost_price

    @api.model
    def get_list_product_on_sale_order(self):
        sale_order_lines = self.order_line or []
        product_ids = []
        for sale_order_line in sale_order_lines:
            product_ids.append(
                (sale_order_line.product_id.id, sale_order_line.location_id.id)
            )
        return product_ids

    @api.multi
    def create_exchange_order(self):
        for order in self:
            if order.exchange_order:
                continue
            new_exchange_order_id = self.env['sale.order'].create({
                'partner_id': order.partner_id.id,
                'exchange_order': True,
                'original_order': order.id,
            })
            if new_exchange_order_id:
                order.write({'exchange_order': True})

    @api.multi
    def create_invoices(self):
        self.ensure_one()
        if self.invoice_status != 'to invoice':
            raise UserError(_('The selected Sales Order should '
                              'contain something to invoice.'))
        adv_wiz = self.env['sale.advance.payment.inv'].with_context(
            active_ids=[self.id]).create({
                'advance_payment_method': 'delivered'})
        adv_wiz.create_invoices()

    @api.model
    def get_stock_quant_for_product(self):
        products = self.get_list_product_on_sale_order()
        product_ids = []
        for product in products:
            product_ids.append(product[0])
        stock_quants = self.env['stock.quant'].search(
            [('product_id', 'in', product_ids),
             ('location_id.usage', '=', 'internal')]
        )
        stock_quant_products = {}
        for stock_quant in stock_quants:
            if (stock_quant.product_id.id, stock_quant.location_id.id)\
                    in products:
                stock_quant_products[stock_quant.id] = True
            else:
                stock_quant_products[stock_quant.id] = False
        return stock_quant_products

    @api.multi
    def action_view_stock_quant(self):
        self.ensure_one()
        context = dict(self._context) or {}
        sale_location_obj = self.env['sale.location.selection']

        stock_quant_products = self.get_stock_quant_for_product()
        for stock_quant_id, selected_location in stock_quant_products.items():
            vals = {
                'stock_quant_id': stock_quant_id,
                'selected_location': selected_location
            }
            sale_location_obj |= sale_location_obj.create(vals)
        view = self.env.ref(
            'kingsport_module.view_sale_location_selection_tree')

        context.update({
            'current_sale_order': self.id,
            'active_mode': self._name,
            'active_id': self.id,
            'search_default_groupby_product_id': True
        })
        return {
            'name': 'Choose Location',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.location.selection',
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': view.id,
            'domain': [('id', 'in', sale_location_obj.ids)],
            'target': 'current',
            'context': context
        }
