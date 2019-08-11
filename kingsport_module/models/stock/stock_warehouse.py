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
from odoo import models, api
import logging
from odoo.addons.sale_rental.models import stock
logger = logging.getLogger(__name__)


@api.multi
def write(self, vals):
    '''
        Change location name from fix to flexible(using ir config parameter)
    '''
    if 'rental_allowed' in vals:
        rental_route = self.env.ref('sale_rental.route_warehouse0_rental')
        sell_rented_route = self.env.ref(
            'sale_rental.route_warehouse0_sell_rented_product')
        if vals.get('rental_allowed'):
            for warehouse in self:
                # Add locations for rental
                warehouse.update_location_rental()
                warehouse.write({
                    'route_ids': [(4, rental_route.id)],
                    'rental_route_id': rental_route.id,
                    'sell_rented_product_route_id': sell_rented_route.id
                })
                # Create rules for warehouse
                for obj, rules_list in\
                        warehouse._get_rental_push_pull_rules().items():
                    for rule in rules_list:
                        warehouse.env[obj].create(rule)
        else:
            # remove rules
            for warehouse in self:
                warehouse.remove_stock_rule_for_rental()
                warehouse.write({
                    'route_ids': [(3, rental_route.id)],
                    'rental_route_id': False,
                    'sell_rented_product_route_id': False,
                })
    return super(stock.StockWarehouse, self).write(vals)


# Replace function write of model StockWarehouse in module sale_rental
stock.StockWarehouse.write = write


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    @api.model
    def update_stock_location_for_rental(self, parent, name):
        '''
            Check stock location for rental alredy exits:
            If not exits: create new stock location for rental
            Param::
                parent: Rental or (Rental in, Rental Out)
                name: name of location(get from ir config parameter)
            Return: Stock Location
        '''
        slo = self.env['stock.location']
        location_view = self.view_location_id
        # search theo name để kiểm tra đã tồn tại location hay chưa
        if parent:  # view Rental
            location = slo.search(
                [('name', '=', name),
                 ('location_id', '=', location_view.id),
                 ('usage', '=', 'view')], limit=1)
            if not location:
                location = slo.create({
                    'name': name,
                    'location_id': location_view.id,
                    'usage': 'view',
                })
                logger.debug(
                    'New view rental stock location created ID %d',
                    location.id)
        else:  # Rental In, Rental Out
            location = slo.search(
                [('name', '=', name),
                 ('location_id', '=', self.rental_view_location_id.id),
                 ('usage', '=', 'view')], limit=1)
            if not location:
                location = slo.create({
                    'name': name,
                    'location_id': self.rental_view_location_id.id,
                    'usage': 'view',
                })
                logger.debug(
                    'New view rental stock location created ID %d',
                    location.id)
        return location

    @api.model
    def update_location_rental(self):
        '''
            Add stock location(rental, rental in, rental out) for warehouse
        '''
        if not self.rental_view_location_id:
            name_rental = self.env['ir.config_parameter'].get_param(
                'name_rental', '')
            location = self.update_stock_location_for_rental(
                parent=True, name=name_rental)
            self.rental_view_location_id = location.id
        if not self.rental_in_location_id:
            name_rental_in = self.env['ir.config_parameter'].get_param(
                'name_rental_in', '')
            location = self.update_stock_location_for_rental(
                parent=False, name=name_rental_in)
            self.rental_in_location_id = location.id
        if not self.rental_out_location_id:
            name_rental_out = self.env['ir.config_parameter'].get_param(
                'name_rental_out', '')
            location = self.update_stock_location_for_rental(
                parent=False, name=name_rental_out)
            self.rental_out_location_id = location.id
        return True

    @api.model
    def remove_stock_rule_for_rental(self):
        '''
            Unlink stock rule for sale rental in warehouse
        '''
        pull_rules_to_delete = self.env['stock.rule'].search(
            [
                ('route_id', 'in', (
                    self.rental_route_id.id,
                    self.sell_rented_product_route_id.id)),
                ('location_src_id', 'in', (
                    self.rental_out_location_id.id,
                    self.rental_in_location_id.id)),
                ('action', '=', 'pull')])
        pull_rules_to_delete.unlink()
        push_rule_to_delete =\
            self.env['stock.rule'].search([
                ('route_id', '=', self.rental_route_id.id),
                ('location_src_id', '=',
                    self.rental_out_location_id.id),
                ('location_id', '=',
                    self.rental_in_location_id.id)])
        push_rule_to_delete.unlink()
        return True
