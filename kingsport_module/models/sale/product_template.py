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
from odoo import api, models, fields
from odoo.exceptions import ValidationError

TYPE_MEMBERSHIP = [
    ('gym', 'Gym Service'),
    ('personal_trainer', 'Personal Trainer Service')
]


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    business_category_id = fields.Many2one(
        'business.category', 'Business category')
    internal_name = fields.Char()
    product_specification = fields.Text()
    origin = fields.Char()
    warranty = fields.Integer()
    type_membership = fields.Selection(
        selection=TYPE_MEMBERSHIP,
        string='Type of Membership', required=True, default='gym')
    month_membership = fields.Integer(
        'Month Membership')
    day_membership = fields.Integer(
        'Days of Training Session')

    @api.constrains('month_membership')
    def _check_month_membership(self):
        for rec in self:
            if rec.month_membership < 0:
                raise ValidationError(
                    _('`Month Membership` should be positive!'))
