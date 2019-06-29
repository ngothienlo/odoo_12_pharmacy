from dateutil.relativedelta import relativedelta

from odoo import fields, models, api, _
from odoo.addons import decimal_precision as dp  # @UnresolvedImport
from odoo.exceptions import UserError, ValidationError

from .membership_line_reserve import MAX_RESERVE_DAYS


class MembershipLine(models.Model):
    _inherit = "membership.membership_line"

    card_number = fields.Char(
        string='Card Number', required=True)
    user_id = fields.Many2one(
        'res.users', string='Salesperson')
    gym_location_id = fields.Many2one(
        'stock.location.gym', string='Gym')
    showroom_id = fields.Many2one(
        'stock.location', string='Showroom',
        domain=[('usage', '=', 'internal')])
    reserve_ids = fields.One2many(
        'membership.line.reserve', 'membership_line_id',
        string='Reservation List')
    stop_membership = fields.Boolean(
        'Stop')
    date_stop = fields.Date('Date Stop')
    days_used = fields.Integer(
        'Days Used', compute='_compute_amount_refunded', store=True)
    amount_refunded = fields.Float(
        'Amount Refunded', digits=dp.get_precision('Product Price'),
        compute='_compute_amount_refunded', store=True)
    invoice_refund_id = fields.Many2one(
        'account.invoice', string='Credit Note', readonly=True,
        ondelete='cascade')

    # Override fields
    date_to = fields.Date(compute='_compute_date_to', store=True)

    @api.model
    def create(self, values):
        if self._context.get('from_membership_invoice', False):
            values.update({
                'user_id': self._context.get('membership_user_id'),
                'gym_location_id': self._context.get(
                    'membership_gym_location_id'),
                'showroom_id': self._context.get('membership_showroom_id'),
                'card_number': self._context.get('membership_card_number')
            })
        if not self._context.get('date_from'):
            values.update({
                'date_from': fields.Date.today()
            })
        return super(MembershipLine, self).create(values)

    @api.constrains('reserve_ids',
                    'reserve_ids.date_from', 'reserve_ids.date_to')
    def _check_total_time_reserve(self):
        """
        - Total reserve time should not exceed 6 months!
        """
        for rec in self:
            dates_reserve = rec.reserve_ids.total_reserve_days()
            if dates_reserve > MAX_RESERVE_DAYS:
                raise ValidationError(
                    _('Total reserve time should not exceed '
                      '%d months!' % (MAX_RESERVE_DAYS / 30)))

    @api.constrains('date_from', 'date_stop')
    def _check_date_stop(self):
        for rec in self:
            if rec.date_stop < rec.date_from:
                raise ValidationError(
                    _('Date Stop should not less than Date From!'))

    @api.depends('date_from', 'date_to', 'membership_id', 'reserve_ids',
                 'reserve_ids.date_from', 'reserve_ids.date_to')
    def _compute_date_to(self):
        for rec in self:
            dates_reserve = rec.reserve_ids.total_reserve_days()

            date_from = fields.Date.from_string(rec.date_from)
            date_to = date_from + relativedelta(
                months=rec.membership_id.month_membership,
                days=dates_reserve)
            rec.date_to = fields.Date.to_string(date_to)

    @api.depends('date_stop', 'stop_membership')
    def _compute_amount_refunded(self):
        for rec in self:
            if not rec.stop_membership or not rec.date_stop or \
                    not rec.account_invoice_id:
                continue

            # Determine exact date_stop
            in_period_reserve = rec.reserve_ids.filtered(
                lambda reserve:
                reserve.date_to >= rec.date_stop >= reserve.date_from)
            if in_period_reserve:
                date_stop = fields.Date.from_string(
                    in_period_reserve[0].date_from)
            else:
                date_stop = fields.Date.from_string(rec.date_stop)

            # Calculate days used
            past_reserves = rec.reserve_ids.filtered(
                lambda reserve: reserve.date_to < rec.date_stop)
            dates_reserve = past_reserves.total_reserve_days()
            date_from = fields.Date.from_string(rec.date_from)
            days_used = (date_stop - date_from).days - dates_reserve

            total_days = rec.membership_id.month_membership * 30
            total_amount = rec.account_invoice_id.amount_total

            rec.amount_refunded = rec.calculate_amount_refunded(
                total_amount, total_days, days_used)
            rec.days_used = days_used

    @api.model
    def calculate_amount_refunded(self, total_amount, total_days, days_used):
        amount_used = (total_amount / total_days) * days_used
        amount_refunded = total_amount - amount_used
        return amount_refunded

    @api.multi
    def button_account_invoice_refund(self):
        self.ensure_one()
        if not self.account_invoice_line:
            raise UserError(_('There is no Invoice for creating Credit Note!'))

        context = {
            'refund_from_membership_line_form': True,
            'active_id': self.account_invoice_id.id,
            'active_ids': [self.account_invoice_id.id],
            'account_invoice_line': self.account_invoice_line.id,
            'amount_refunded': self.amount_refunded
        }
        return {
            'name': _("Credit Note for Membership"),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.invoice.refund',
            'view_id': self.env.ref('account.view_account_invoice_refund').id,
            'target': 'new',
            'context': context
        }
