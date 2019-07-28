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


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    @api.depends('line_ids.theoretical_qty', 'line_ids.product_qty')
    def _compute_check_different_inventory(self):
        for rec in self:
            # Check is different inventory
            for line in rec.line_ids:
                if line.theoretical_qty != line.product_qty:
                    rec.is_different_in_inventory_detail = True
                    break

    is_different_in_inventory_detail = fields.Boolean(
        compute='_compute_check_different_inventory',
        string='Difference in details')

    def action_validate(self):
        if self.is_different_in_inventory_detail:
            if not self.env.user.has_group('stock.group_stock_manager'):
                raise Warning(_('There is a difference in detail, please '
                                'ask for validation from inventory manager!'))
        return super(StockInventory, self).action_validate()
