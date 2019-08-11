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
from datetime import date

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

    @api.multi
    def create_membership_invoice(self, product_id=None, datas=None):
        """
        Override to update description on account.move.line
        """
        invoice_list = super(ResPartner, self).\
            create_membership_invoice(product_id, datas)

        if not self._context.get('from_membership_invoice', False)\
                or not invoice_list:
            return invoice_list

        invoices = self.env['account.invoice'].browse(invoice_list)
        for partner in self:
            invoice = invoices.filtered(lambda i: i.partner_id == partner)
            card_number = self._context.get('membership_card_number', '')
            for line in invoice.invoice_line_ids:
                line.write({'name': '%s : %s' % (
                    card_number,
                    line.product_id and line.product_id.name or '')})
        return invoice_list

    def _membership_state(self):
        """
        This Function return Membership State For Given Partner.
        Override to update the way finding refund invoice
        """
        res = {}
        today = fields.Date.context_today(self)
        invoice_obj = self.env['account.invoice']
        for partner in self:
            res[partner.id] = 'none'

            if partner.membership_cancel and today > partner.membership_cancel:
                res[partner.id] = 'free' if partner.free_member else 'canceled'
                continue
            if partner.membership_stop and today > partner.membership_stop:
                res[partner.id] = 'free' if partner.free_member else 'old'
                continue
            if partner.associate_member:
                res_state = partner.associate_member._membership_state()
                res[partner.id] = res_state[partner.associate_member.id]
                continue

            s = 4
            if partner.member_lines:
                for mline in partner.member_lines:
                    if (mline.date_to or date.min) >= today and (
                            mline.date_from or date.min) <= today:
                        if mline.account_invoice_line.invoice_id.\
                                partner_id == partner:
                            mstate =\
                                mline.account_invoice_line.invoice_id.state
                            if mstate == 'paid':
                                s = 0
                                invoice = mline.account_invoice_line.invoice_id
                                if invoice:
                                    refund_invoices = invoice_obj.search([
                                        ('type', '=', 'out_refund'),
                                        ('origin', '=', invoice.number),
                                        ('state', '=', 'paid')], limit=1)
                                    if refund_invoices:
                                        s = 2
                                break
                            elif mstate == 'open' and s != 0:
                                s = 1
                            elif mstate == 'cancel' and s != 0 and s != 1:
                                s = 2
                            elif mstate == 'draft' and s != 0 and s != 1:
                                s = 3
                if s == 4:
                    for mline in partner.member_lines:
                        if (mline.date_from or date.min) < today and (
                                mline.date_to or date.min) < today and (
                                mline.date_from or date.min) <= (
                                mline.date_to or date.min) and \
                                mline.account_invoice_line and \
                                mline.account_invoice_line.invoice_id.\
                                state == 'paid':
                            s = 5
                        else:
                            s = 6
                if s == 0:
                    res[partner.id] = 'paid'
                elif s == 1:
                    res[partner.id] = 'invoiced'
                elif s == 2:
                    res[partner.id] = 'canceled'
                elif s == 3:
                    res[partner.id] = 'waiting'
                elif s == 5:
                    res[partner.id] = 'old'
                elif s == 6:
                    res[partner.id] = 'none'
            if partner.free_member and s != 0:
                res[partner.id] = 'free'
        return res
