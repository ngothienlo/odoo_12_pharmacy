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
import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    partner_id = fields.Many2one()
    phone = fields.Char(required=True)
    active = fields.Boolean(copy=False)
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
    team_id = fields.Many2one(
        compute='_compute_assign_team', readonly=False, store=True)
    is_wrong_address = fields.Boolean()

    @api.multi
    def _compute_activity_history_count(self):
        for lead in self:
            lead.activity_history_count = self.env['activity.history'].\
                search_count([
                    ('crm_lead_id', '=', lead.id)])

    @api.constrains('phone', 'type', 'active')
    def _is_validate_phone(self):
        if self.search_count(
                [('phone', '=', self.phone), ('id', '!=', self.id),
                 ('type', '!=', 'opportunity'), ('active', '=', True)]):
            _logger.error('======CRM.LEAD: Phone number already exists=======')
            raise ValidationError(
                _('This phone number already exists in the system. \n'
                  'Please input another phone number.'))

    @api.depends('district_id')
    def _compute_assign_team(self):
        for lead in self:
            if lead.district_id:
                lead.team_id = lead.get_assign_allocation()
            else:
                lead.team_id = False

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

    def _onchange_partner_id_values(self, partner_id):
        """ returns the new values when partner_id has changed """
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)

            partner_name = partner.parent_id.name
            if not partner_name and partner.is_company:
                partner_name = partner.name

            new_vals = {
                'district_id': partner.district_id.id,
                'ward_id': partner.ward_id.id,
            }
            vals = super(CrmLead, self)._onchange_partner_id_values(partner_id)
            vals.update(new_vals)
            return vals
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
    def write(self, vals):
        res = super(CrmLead, self).write(vals)
        for lead_opp in self:
            new_vals, is_wrong_address = lead_opp._check_address(
                vals.get('country_id') or lead_opp.country_id.id,
                vals.get('state_id') or lead_opp.state_id.id,
                vals.get('district_id') or lead_opp.district_id.id,
                vals.get('ward_id') or lead_opp.ward_id.id)
            new_vals['is_wrong_address'] = is_wrong_address
            super(CrmLead, lead_opp).write(new_vals)
        return res

    @api.model
    def get_formview_id_on_kanban(self, access_uid=None):
        if self._context.get('default_type') == 'opportunity':
            view_id = self.env.ref('crm.crm_case_form_view_oppor').id
        else:
            view_id = super(CrmLead, self).get_formview_id()
        return view_id

    def _check_address(self, c_id, s_id, d_id, w_id):
        addr_vals = {}
        is_wrong_address = False
        country = self.env['res.country'].browse(c_id)
        state = self.env['res.country.state'].browse(s_id)
        district = self.env['res.country.state.district'].browse(d_id)
        ward = self.env['res.country.state.district.ward'].browse(w_id)
        if (not country and state) or \
                (country and state and
                 state.country_id.id != (country and country.id or False)):
            state = addr_vals['state_id'] = False
            is_wrong_address = True
        if (not state and district) or \
                (state and district and
                 district.state_id.id != (state and state.id or False)):
            district = addr_vals['district_id'] = False
            is_wrong_address = True
        if (not district and ward) or \
                (district and ward and
                 ward.district_id.id != (district and district.id or False)):
            ward = addr_vals['ward_id'] = False
            is_wrong_address = True
        return addr_vals, is_wrong_address

    @api.multi
    def _prepare_vals(self, vals):
        if 'partner_id' in vals:
            partner_id = self.env['res.partner'].browse(vals.get('partner_id'))
            if not vals.get('gender'):
                vals['gender'] = partner_id.gender
            if not vals.get('birthday'):
                vals['birthday'] = partner_id.birthday
            if not vals.get('country_id'):
                vals['country_id'] = partner_id.country_id.id
            if not vals.get('state_id'):
                vals['state_id'] = partner_id.state_id.id
            if not vals.get('district_id'):
                vals['district_id'] = partner_id.district_id.id
            if not vals.get('ward_id'):
                vals['ward_id'] = partner_id.ward_id.id
        new_vals, is_wrong_address = self._check_address(
            vals.get('country_id'), vals.get('state_id'),
            vals.get('district_id'), vals.get('ward_id'))
        new_vals['is_wrong_address'] = is_wrong_address
        vals.update(new_vals)
        return vals

    @api.multi
    def _create_lead_partner_data(self, name, is_company, parent_id=False):
        partner_values = super(CrmLead, self)._create_lead_partner_data(
            name, is_company, parent_id)
        partner_values.update({
            'district_id': self.district_id.id,
            'ward_id': self.ward_id.id
        })
        return partner_values
