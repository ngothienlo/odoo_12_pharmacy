from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    month_membership = fields.Integer(
        'Month Membership')

    @api.constrains('month_membership')
    def _check_month_membership(self):
        for rec in self:
            if rec.month_membership < 0:
                raise UserError(_('`Month Membership` should be positive!'))
