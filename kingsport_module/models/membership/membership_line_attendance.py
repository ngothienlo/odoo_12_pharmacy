from odoo import api, fields, models


class MembershipLineAttendance(models.Model):
    _name = 'membership.line.attendance'
    _order = 'date_training desc'

    date_training = fields.Date(
        string='Date Training', default=fields.Date.context_today)
    personal_trainer_id = fields.Many2one(
        'res.users', string='Personal Trainer')
    membership_line_id = fields.Many2one(
        'membership.membership_line', string='Membership Line',
        required=True, ondelete='cascade')

    @api.model
    def default_get(self, default_fields):
        """ Compute default partner_bank_id field for 'out_invoice' type,
        using the default values computed for the other fields.
        """
        res = super(MembershipLineAttendance, self).default_get(default_fields)
        return res
