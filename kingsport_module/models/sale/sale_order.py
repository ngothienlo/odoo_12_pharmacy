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
from odoo.exceptions import Warning


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _get_default_locaiton(self):
        return self.env.user.location_id or False

    @api.model
    def _default_approval(self):
        return self.env.user.partner_id.id or False

    approval_id = fields.Many2one(
        'res.partner', 'Approver',
        domain=[('customer', '=', False), ('supplier', '=', False)],
        default=lambda self: self._default_approval(),
        track_visibility='onchange')
    direct_shipping = fields.Boolean()
    location_id = fields.Many2one(
        'stock.location', 'Delivery Location',
        default=lambda self: self._get_default_locaiton(),
        domain=[('usage', '=', 'internal'), ('is_sale_location', '=', True)])
    is_maintenance_order = fields.Boolean('Maintenance Order', copy=False)
    delivery_order_id = fields.Many2one(
        'stock.picking', 'Delivery Order', copy=False)
    is_exchange_order = fields.Boolean('Exchange Order', copy=False)
    original_order_id = fields.Many2one(
        'sale.order', 'Original Order', copy=False)
    total_cost_price = fields.Monetary(
        compute='_compute_total_cost_price', store=True)
    contact_name = fields.Char(
        'Shipping Contact',
        related='partner_shipping_id.name',
        required=True, store=True, readonly=False, copy=True)
    phone = fields.Char(
        'Contact Phone',
        related='partner_shipping_id.phone',
        required=True, store=True, readonly=False)
    district_id = fields.Many2one(
        related='partner_shipping_id.district_id',
        required=True, store=True, readonly=False)
    ward_id = fields.Many2one(
        related='partner_shipping_id.ward_id',
        required=True, store=True, readonly=False)
    street = fields.Char(
        related='partner_shipping_id.street',
        required=True, store=True, readonly=False)
    street2 = fields.Char(
        related='partner_shipping_id.street2', store=True, readonly=False)
    country_id = fields.Many2one(
        related='partner_shipping_id.country_id',
        required=True, store=True, readonly=False, copy=True)
    state_id = fields.Many2one(
        related='partner_shipping_id.state_id',
        required=True, store=True, readonly=False, copy=True)
    partner_shipping_id = fields.Many2one(
        domain="['|', ('parent_id', '=', partner_id),"
               "('id','=', partner_id)]", required=False)
    current_location_id = fields.Many2one(
        'stock.location', 'Current Location',
        default=lambda self: self._get_default_locaiton())
    is_rental_order = fields.Boolean('Rental Order', default=False)
    note_service = fields.Text(
        'Note For Service', default=lambda self: self._default_note_service())
    note_payment_method = fields.Text(
        'Note Payment Method',
        default=lambda self: self._default_note_payment_method())
    note_delivery_method = fields.Text(
        'Note Delivery Method',
        default=lambda self: self._default_note_delivery_method())
    note = fields.Text(
        'Sale Note', default=lambda self: self._default_sale_note()
    )

    @api.model
    def _default_sale_note(self):
        return self.env.user.company_id and\
            self.env.user.company_id.sale_note or ''

    @api.model
    def _default_note_service(self):
        return self.env.user.company_id and\
            self.env.user.company_id.note_service or ''

    @api.model
    def _default_note_payment_method(self):
        return self.env.user.company_id and\
            self.env.user.company_id.note_payment_method or ''

    @api.model
    def _default_note_delivery_method(self):
        return self.env.user.company_id and\
            self.env.user.company_id.note_delivery_method or ''

    @api.depends('order_line.total_cost')
    def _compute_total_cost_price(self):
        for rec in self:
            sale_order_lines = rec.order_line.filtered(
                lambda line: line.display_type not in (
                    'line_section', 'line_note')) or []
            total_cost_price = 0.0
            for sale_order_line in sale_order_lines:
                total_cost = sale_order_line.total_cost or 0.0
                total_cost_price += total_cost
            rec.total_cost_price = total_cost_price

    @api.model
    def get_list_product_on_sale_order(self):
        sale_order_lines = self.order_line.filtered(
            lambda line: line.display_type not in
            ('line_section', 'line_note') and line.product_id.type == 'product'
        ) or []
        product_ids = []
        for sale_order_line in sale_order_lines:
            product_ids.append(
                (sale_order_line.product_id, sale_order_line.location_id)
            )
        return product_ids

    @api.multi
    def create_exchange_order(self):
        self.ensure_one()
        new_exchange_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'is_exchange_order': True,
            'original_order_id': self.id,
            'contact_name': self.contact_name,
            'street': self.street,
            'street2': self.street2,
            'phone': self.phone,
            'district_id': self.district_id.id,
            'ward_id': self.ward_id.id,
            'country_id': self.country_id.id,
            'state_id': self.state_id.id,
        })
        if new_exchange_order:
            return {
                'name': _('Exchange Order'),
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': new_exchange_order.id,
                'target': 'current'
            }

    @api.multi
    def create_invoices(self):
        self.ensure_one()
        if self.invoice_status != 'to invoice':
            raise UserError(_('The selected Sales Order should '
                              'contain something to invoice.'))
        adv_wiz = self.env['sale.advance.payment.inv'].with_context(
            active_ids=[self.id]).create({
                'advance_payment_method': 'delivered'})
        return adv_wiz.with_context(open_invoices=True).create_invoices()

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        invoices = super(SaleOrder, self).action_invoice_create(
            grouped=False, final=False)
        for invoice_id in invoices:
            if self.is_exchange_order:
                ivn_line_env = self.env['account.invoice.line']
                ivn_line_env.create({
                    'name': _('Exchanged Order for SO %s') % (
                        self.original_order_id and
                        self.original_order_id.name),
                    'display_type': 'line_note',
                    'invoice_id': invoice_id
                })
        return invoices

    @api.model
    def get_stock_quant_for_product(self):
        products = self.get_list_product_on_sale_order()
        product_ids = []
        for product in products:
            product_ids.append(product[0].id)
        stock_quants = self.env['stock.quant'].search(
            [('product_id', 'in', product_ids),
             ('location_id.usage', '=', 'internal'),
             ('location_id.is_sale_location', '=', True)]
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
            'search_default_groupby_product_id': True,
        })
        return {
            'name': _('Choose Location'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.location.selection',
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': view.id,
            'domain': [('id', 'in', sale_location_obj.ids)],
            'target': 'current',
            'context': context
        }

    @api.multi
    def _create_shipping_address(self):
        partner_env = self.env['res.partner']
        for rec in self:
            if not rec.partner_shipping_id:
                # Create shipping address for partner_id current
                vals = {
                    'type': 'delivery',
                    'street': rec.street,
                    'street2': rec.street2 or '',
                    'country_id': rec.country_id.id,
                    'district_id': rec.district_id.id,
                    'state_id': rec.state_id.id,
                    'ward_id': rec.ward_id.id,
                    'name': rec.contact_name,
                    'phone': rec.phone,
                    'parent_id': rec.partner_id.id,
                }
                partner = partner_env.create(vals)
                rec.partner_shipping_id = partner
        return True

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        res._create_shipping_address()
        return res

    @api.multi
    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        self._create_shipping_address()
        return res

    @api.multi
    def action_create_down_payment(self):
        self.ensure_one()
        memo = _('%s - Down payment') % (self.name)
        context = {
            'default_payment_type': 'inbound',
            'default_partner_type': 'customer',
            'default_partner_id': self.partner_id.id or False,
            'default_communication': memo,
            'is_payment_from_so': True
        }
        return {
            'name': _('Create Down Payment'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
            'context': context
        }

    @api.onchange('user_id')
    def _domain_sale_person(self):
        sale_team = self.user_id and self.user_id.sale_team_id or False
        self.team_id = sale_team

    @api.onchange('team_id')
    def _onchange_team_id(self):
        member_ids = self.team_id and self.team_id.member_ids and\
            self.team_id.member_ids.ids or False
        domain = {}
        if member_ids:
            domain['user_id'] = [('id', 'in', member_ids)]
            return {'domain': domain}
        else:
            domain['user_id'] = []
            return {'domain': domain}

    @api.multi
    def _create_internal_tranfer(self):
        self.ensure_one()
        lines = self.order_line.filtered(
            lambda line: line.display_type not in
            ('line_section', 'line_note') and line.product_id.type == 'product'
        ) or []
        if not self.current_location_id:
            raise Warning(
                _('Current showroom is not defined. Please  define '
                  'it in tab other information of user form.'))
        for line in lines:
            if line.location_id != self.current_location_id:
                line._create_stock_move()
        return True

    @api.multi
    def action_confirm(self):
        # check exist approver
        if not self.approval_id:
            raise Warning(_('Need to specify a approver quotations'))
        # check s.o line none location => raise warning
        self.check_sale_order_line_none_location()
        direct_shipping = self.direct_shipping
        if not direct_shipping and not self.is_rental_order:
            self._create_internal_tranfer()
        res = super(SaleOrder, self).action_confirm()
        return res

    @api.multi
    def check_sale_order_line_none_location(self):
        product_ids = self.get_list_product_on_sale_order()
        product_name = []
        for product in product_ids:
            if not product[1]:
                product_name.append(product[0].name)
        product_name_str = ', '.join(product_name)
        if len(product_name) > 0:
            raise Warning(
                _('Need to specify a stock for product: "%s"!')
                % product_name_str)
        return True
