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


class ResPartner(models.Model):
    _inherit = 'res.partner'

    birthday = fields.Date('Date of Birth')
    gender = fields.Selection(
        selection=[('female', 'Female'),
                   ('male', 'Male'),
                   ('other', 'Other')])
    source = fields.Char()
    district_id = fields.Many2one(
        'res.country.state.district', string="District",
        domain="[('state_id', '=', state_id)]")
    ward_id = fields.Many2one(
        'res.country.state.district.ward', string="Ward",
        domain="[('district_id', '=', district_id)]")

    _sql_constraints = [
        ('phone_unique', 'unique(phone)',
         ('This phone number already exists in the system. \n'
          'Please input another phone number.'))
    ]

    @api.multi
    def _display_address(self, without_company=False):
        '''
        The purpose of this function is to build and
        return an address formatted accordingly to the
        standards of the country where it belongs.

        :param address: browse record of the res.partner to format
        :returns: the address formatted in a display that
            fit its country habits (or the default ones
            if not country is specified)
        :rtype: string
        '''
        # get the information that will be injected into the display format
        # get the address format
        address_format = self._get_address_format()
        args = {
            'state_code': self.state_id.code or '',
            'state_name': self.state_id.name or '',
            'country_code': self.country_id.code or '',
            'country_name': self._get_country_name(),
            'company_name': self.commercial_company_name or '',
            'ward_name': self.ward_id.name or '',
            'district_name': self.district_id.name or '',
        }
        for field in self._formatting_address_fields():
            args[field] = getattr(self, field) or ''
        if without_company:
            args['company_name'] = ''
        elif self.commercial_company_name:
            address_format = '%(company_name)s\n' + address_format
        return address_format % args

    def _display_address_depends(self):
        # field dependencies of method _display_address()
        return super(ResPartner, self)._display_address_depends() + [
            'district_id.name', 'ward_id.name']

    @api.model
    def _address_fields(self):
        return super(ResPartner, self)._address_fields() +\
            ['ward_id', 'district_id']
