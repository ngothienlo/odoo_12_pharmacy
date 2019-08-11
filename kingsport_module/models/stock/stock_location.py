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
    is_sale_location = fields.Boolean('Sale Location')
    showroom_name = fields.Char(
        compute='_get_showroom_name', readonly=False, store=True)

    @api.depends('name')
    def _get_showroom_name(self):
        for rec in self:
            rec.showroom_name = rec.name or ''

    @api.multi
    def name_get(self):
        context = dict(self._context) or {}
        params = context and context.get('params', {}) or {}
        model_call = params and params.get('model', '') or ''
        calling_from_so = model_call and model_call == 'sale.order' or False
        default_is_rental_order = context.get('default_is_rental_order', False)
        if context.get('display_showroom_name', False)\
                or calling_from_so or default_is_rental_order:
            result = []
            for rec in self:
                name = "%s %s" % ('CN', rec.showroom_name or '')
                result.append((rec.id, name))
            return result
        return super(StockLocation, self).name_get()

    @api.onchange('usage')
    def _reset_config_location(self):
        ''' If usge != internal
            Reset allow_to_receive_good and is_sale_location = False'''
        self.allow_to_receive_good = False
        self.is_sale_location = False

    @api.model
    def name_search(self, name, args=None, operator='like', limit=100):
        args = args or []
        domain = []
        context = dict(self._context) or {}
        code = context.get('code', False)
        if name:
            domain = ['|', ('name', operator, name),
                      ('showroom_name', operator, name)]
        if code and code == 'incoming':
            domain.append(('allow_to_receive_good', '=', True))
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()
