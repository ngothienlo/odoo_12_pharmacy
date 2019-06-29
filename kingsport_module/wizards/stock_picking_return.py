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
from datetime import datetime


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _create_returns(self):
        new_picking_id, picking_type_id = super(
            ReturnPicking, self)._create_returns()
        if self.picking_id.state == 'done' and (
                datetime.now().date() -
                self.picking_id.date_done.date()).days > 7:
            self.env['stock.picking'].browse(
                new_picking_id).write({'return_do_over_7days': True})
        return new_picking_id, picking_type_id

    @api.model
    def default_get(self, fields_):
        res = super(ReturnPicking, self).default_get(fields_)
        if 'product_reodturn_moves' in res:
            for line in res.get('product_reodturn_moves'):
                line[2].update({'to_refund': True})
        return res
