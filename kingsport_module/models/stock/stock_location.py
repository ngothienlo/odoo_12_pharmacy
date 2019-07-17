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


class StockLocation(models.Model):
    _inherit = 'stock.location'

    allow_to_receive_good = fields.Boolean()

    @api.model
    def name_search(self, name, args=None, operator='like', limit=100):
        args = args or []
        domain = []
        context = dict(self._context) or {}
        code = context.get('code', False)
        if name:
            domain = [('name', operator, name)]
        if code and code == 'incoming':
            domain.append(('allow_to_receive_good', '=', True))
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()
