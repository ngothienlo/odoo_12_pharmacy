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
from odoo import api, fields, models


class AuthorizedApproval(models.TransientModel):
    _name = 'authorized.approval'
    _inherit = "mail.thread"

    approver_id = fields.Many2one(
        'res.partner', 'Authorized Approver', required=True,
        domain=[('customer', '=', False), ('supplier', '=', False)])

    @api.multi
    def authorized_approval(self):
        self.ensure_one()
        stock_picking_env = self.env['stock.picking']
        context = dict(self._context) or {}
        stock_picking_id = context.get('default_stock_picking_id', False)
        if stock_picking_id:
            stock_picking = stock_picking_env.search(
                [('id', '=', stock_picking_id)], limit=1)
            stock_picking.approver_id = self.approver_id
            stock_picking.action_confirm()
            stock_picking.action_assign()
            stock_picking.write({'approver_id': self.approver_id.id})
        return True
