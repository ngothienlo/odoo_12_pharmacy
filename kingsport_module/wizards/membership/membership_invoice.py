from odoo import api, fields, models


class MembershipInvoice(models.TransientModel):
    _inherit = "membership.invoice"

    card_number = fields.Char(
        string='Card Number', required=True)
    user_id = fields.Many2one(
        'res.users', string='Salesperson',
        default=lambda self: self.env.user)
    gym_location_id = fields.Many2one(
        'stock.location.gym', string='Gym')
    showroom_id = fields.Many2one(
        'stock.location', string='Showroom',
        domain=[('usage', '=', 'internal')])
    personal_trainer_id = fields.Many2one(
        'res.users', string='Personal Trainer')
    type_membership = fields.Selection(
        related='product_id.type_membership')

    @api.onchange('product_id')
    def onchange_product(self):
        """This function returns value of  product's member price based on product id.
        """
        price_dict = self.product_id.price_compute('list_price')
        self.member_price = price_dict.get(self.product_id.id) or False

    @api.onchange('gym_location_id')
    def _onchange_gym_location_id(self):
        if self.gym_location_id:
            self.showroom_id = self.gym_location_id.showroom_id

    @api.multi
    def membership_invoice(self):
        self.ensure_one()
        context = self._context.copy()
        context.update({
            'from_membership_invoice': True,
            'membership_user_id': self.user_id.id,
            'membership_gym_location_id': self.gym_location_id.id,
            'membership_showroom_id': self.showroom_id.id,
            'membership_card_number': self.card_number,
            'membership_personal_trainer_id': self.personal_trainer_id.id})
        self = self.with_context(context)
        action = super(MembershipInvoice, self).membership_invoice()
        return action
