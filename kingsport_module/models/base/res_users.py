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
from odoo import models, api, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    location_id = fields.Many2one('stock.location', 'Showroom')

    @api.model
    def _default_sidebar_type(self):
        return self.env.user.company_id.default_sidebar_preference or\
            'invisible'

    @api.model
    def _default_chatter_position(self):
        return self.env.user.company_id.default_chatter_preference or 'sided'
