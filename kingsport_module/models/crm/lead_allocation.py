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


class LeadAllocation(models.Model):
    _name = 'lead.allocation'

    name = fields.Char(required=True)
    team_id = fields.Many2one('crm.team', string='Team', required=True)
    state_ids = fields.Many2many(
        'res.country.state', string='State', required=True)
    is_main_city = fields.Boolean()
    district_ids = fields.Many2many(
        'res.country.state.district', string='Districts')

    _sql_constraints = [
        ('team_unique', 'unique(team_id)',
         ('This team already exists in the allocation. \n'
          'Please input another team.'))
    ]

    @api.onchange('team_id')
    def onchange_team_id(self):
        all_allo_ids = self.env['lead.allocation'].search([])
        not_avail_district_ids = []
        not_avail_state_ids = []
        if all_allo_ids:
            not_avail_state_ids = all_allo_ids.mapped(
                'state_ids').mapped('id')
            not_avail_district_ids = all_allo_ids.mapped(
                'district_ids').mapped('id')
        self.state_ids = self.district_ids = False
        return {'domain': {
            'district_ids': [
                ('state_id', 'not in', not_avail_state_ids),
                ('id', 'not in', not_avail_district_ids)],
            'state_ids': [('id', 'not in', not_avail_state_ids)]}}

    @api.onchange('state_ids')
    def onchange_state_ids(self):
        all_allo_ids = self.env['lead.allocation'].search([])
        not_avail_district_ids = []
        if all_allo_ids:
            not_avail_district_ids = all_allo_ids.mapped(
                'district_ids').mapped('id')
        return {'domain': {
            'district_ids': [
                ('state_id', 'in', self.state_ids.ids),
                ('id', 'not in', not_avail_district_ids)]}}

    @api.onchange('state_ids')
    def onchange_state_id(self):
        if not self.state_ids:
            self.is_main_city = False
        elif any(city in self.state_ids.ids for city in [
                self.env.ref('l10n_vn_country_state.res_country_state_79').id,
                self.env.ref('l10n_vn_country_state.res_country_state_01').id]
        ):
            self.is_main_city = True
        else:
            self.is_main_city = False
