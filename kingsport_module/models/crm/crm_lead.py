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


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    partner_id = fields.Many2one(required=True)
    phone = fields.Char(required=True)
    category_ids = fields.Many2many(
        'product.category', string='Categories', required=True)
    product_ids = fields.Many2many(
        'product.product', string='Products', required=True)
    birthday = fields.Date()
    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female'), ('other', 'Other'), ], )
    district_id = fields.Many2one(
        'res.country.state.district', string='District',
        domain="[('state_id', '=', state_id)]")
    ward_id = fields.Many2one(
        'res.country.state.district.ward', string='Ward',
        domain="[('district_id', '=', district_id)]")
    activity_history_count = fields.Integer(
        'Activity History',
        compute='_compute_activity_history_count')

    @api.multi
    def _compute_activity_history_count(self):
        for lead in self:
            lead.activity_history_count = self.env['activity.history'].\
                search_count([
                    ('crm_lead_id', '=', lead.id)])

    _sql_constraints = [
        ('phone_unique', 'unique(phone)',
         ('This phone number already exists in the system. \n'
          'Please input another phone number.'))
    ]

    @api.onchange('country_id')
    def on_change_country_id(self):
        self.state_id = False

    @api.onchange('state_id')
    def on_change_state_id(self):
        self.district_id = False

    @api.onchange('district_id')
    def on_change_district_id(self):
        self.ward_id = False
        if self.district_id:
            self.team_id = self.get_assign_allocation()
        else:
            self.team_id = False

    @api.multi
    def get_assign_allocation(self):
        self.ensure_one()
        for allo_id in self.env['lead.allocation'].search([]):
            if self.district_id.id in allo_id.district_ids.ids:
                return allo_id.team_id.id
            else:
                continue
