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


class CrmTeam(models.Model):

    _inherit = 'crm.team'

    parent_id = fields.Many2one('crm.team', String='Parent SalesTeam')

    @api.depends('name', 'parent_id.name')
    def _compute_display_name(self):
        names = dict(self.with_context().name_get())
        for partner in self:
            pre_name = partner.parent_id.display_name and (
                partner.parent_id.display_name + " / ") or ''
            partner.display_name = pre_name + names.get(partner.id)
