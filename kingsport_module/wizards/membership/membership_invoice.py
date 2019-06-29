from odoo import api, fields, models


class MembershipInvoice(models.TransientModel):
    _inherit = "membership.invoice"

    card_number = fields.Char(
        string='Card Number', required=True)
    user_id = fields.Many2one(
        'res.users', string='Salesperson')
    gym_location_id = fields.Many2one(
        'stock.location.gym', string='Gym')
    showroom_id = fields.Many2one(
        'stock.location', string='Showroom',
        domain=[('usage', '=', 'internal')])

    @api.onchange('product_id')
    def onchange_product(self):
        """This function returns value of  product's member price based on product id.
        """
        price_dict = self.product_id.price_compute('list_price')
        self.member_price = price_dict.get(self.product_id.id) or False

    @api.multi
    def membership_invoice(self):
        self.ensure_one()
        context = self._context.copy()
        context.update({
            'from_membership_invoice': True,
            'membership_user_id': self.user_id.id,
            'membership_gym_location_id': self.gym_location_id.id,
            'membership_showroom_id': self.showroom_id.id,
            'membership_card_number': self.card_number})
        self = self.with_context(context)
        action = super(MembershipInvoice, self).membership_invoice()
        return action
