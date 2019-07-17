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

    partner_id = fields.Many2one()
    phone = fields.Char(required=True)
    category_ids = fields.Many2many('product.category', string='Categories')
    product_ids = fields.Many2many('product.product', string='Products')
    birthday = fields.Date()
    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female'), ('other', 'Other'), ], )
    district_id = fields.Many2one(
        'res.country.state.district', string='District',
        domain="[('state_id', '=', state_id)]")
    state_id = fields.Many2one(domain="[('country_id', '=', country_id)]")
    ward_id = fields.Many2one(
        'res.country.state.district.ward', string='Ward',
        domain="[('district_id', '=', district_id)]")
    is_at_main_city = fields.Boolean(related='state_id.is_main_city')
    activity_history_count = fields.Integer(
        'Activity History',
        compute='_compute_activity_history_count')
    country_id = fields.Many2one(
        default=lambda self: self.env[
            'ir.model.data'].xmlid_to_res_id('base.vn'))
    team_id = fields.Many2one(default=False)

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
    def _onchange_state(self):
        self.district_id = False

    @api.onchange('district_id')
    def on_change_district_id(self):
        self.ward_id = False
        if self.district_id:
            self.team_id = self.get_assign_allocation()
        else:
            self.team_id = False

    @api.model
    def _onchange_user_values(self, user_id):
        """Overwrite func for apply Kingsport workflow"""
        if self._name == 'crm.lead':
            return {}
        else:
            return super(CrmLead, self)._onchange_user_values()

    @api.onchange('team_id')
    def _onchange_team_id(self):
        self.user_id = self.team_id and self.team_id.user_id or False

    @api.onchange('user_id')
    def _onchange_user_id(self):
        """Overwrite for Kingsport workflow"""
        return {}

    @api.multi
    def get_assign_allocation(self):
        self.ensure_one()
        for allo_id in self.env['lead.allocation'].search([]):
            if self.district_id.id in allo_id.district_ids.ids:
                return allo_id.team_id.id
            else:
                continue
        return False

    @api.model
    def create(self, vals):
        new_vals = self._prepare_vals(vals)
        res = super(CrmLead, self).create(new_vals)
        return res

    @api.multi
    def _prepare_vals(self, vals):
        if 'partner_id' in vals:
            partner_id = self.env['res.partner'].browse(vals.get('partner_id'))
            if not vals.get('gender'):
                vals['gender'] = partner_id.gender
            if not vals.get('birthday'):
                vals['birthday'] = partner_id.birthday
            if not vals.get('district_id'):
                vals['district_id'] = partner_id.district_id.id
            if not vals.get('ward_id'):
                vals['ward_id'] = partner_id.ward_id.id
        return vals
