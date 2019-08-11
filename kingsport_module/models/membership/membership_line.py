from dateutil.relativedelta import relativedelta

from odoo import fields, models, api, _
from odoo.addons import decimal_precision as dp  # @UnresolvedImport
from odoo.exceptions import UserError, ValidationError

from .membership_line_reserve import MAX_RESERVE_DAYS
from ..sale.product_template import TYPE_MEMBERSHIP


class MembershipLine(models.Model):
    _inherit = 'membership.membership_line'

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
        ondelete='set null')
    type_membership = fields.Selection(
        selection=TYPE_MEMBERSHIP, related='membership_id.type_membership')
    personal_trainer_id = fields.Many2one(
        'res.users', string='Personal Trainer', ondelete='set null')
    day_membership = fields.Integer(
        'Days of Training Session', readonly=True)
    attendance_ids = fields.One2many(
        'membership.line.attendance', 'membership_line_id',
        string='Attendance Training')
    is_expired = fields.Boolean(
        'Is Expired?', compute='_compute_is_expired', store=False)

    # Override fields
    date_to = fields.Date(compute='_compute_date_to', store=True)

    @api.model
    def create(self, values):
        if self._context.get('from_membership_invoice', False):
            values.update({
                'user_id': self._context.get(
                    'membership_user_id', False),
                'gym_location_id': self._context.get(
                    'membership_gym_location_id', False),
                'showroom_id': self._context.get(
                    'membership_showroom_id', False),
                'card_number': self._context.get(
                    'membership_card_number', False),
                'personal_trainer_id': self._context.get(
                    'membership_personal_trainer_id', False)
            })

        membership_id = values.get('membership_id', False)
        membership = self.env['product.product'].browse(membership_id)
        if membership and membership.type_membership == 'personal_trainer':
            values.update({'day_membership': membership.day_membership})

        # Reset date_from, this value will be updated
        # when validate related invoice.
        values.update({'date_from': None})
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
            if rec.date_stop and rec.date_from and \
                    rec.date_stop < rec.date_from:
                raise ValidationError(
                    _('Date Stop should not less than Date From!'))

    @api.constrains('attendance_ids',
                    'membership_id', 'membership_id.day_membership')
    def _check_total_attendances(self):
        for rec in self:
            if rec.membership_id and \
                    len(rec.attendance_ids) > rec.membership_id.day_membership:
                raise ValidationError(
                    _('The total number of training days should not exceed '
                      '%d day(s)!') % (rec.membership_id.day_membership))

    @api.depends('date_from', 'membership_id', 'reserve_ids',
                 'reserve_ids.date_from', 'reserve_ids.date_to')
    def _compute_date_to(self):
        for rec in self:
            dates_reserve = rec.reserve_ids.total_reserve_days()

            if rec.date_from:
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

            total_amount = rec.account_invoice_id.amount_total

            if rec.membership_id.type_membership == 'gym':
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

                rec.amount_refunded =\
                    rec.calculate_amount_refunded_gym_service(
                        total_amount, total_days, days_used)
                rec.days_used = days_used
            elif rec.membership_id.type_membership == 'personal_trainer':
                rec.days_used = len(rec.attendance_ids)
                rec.amount_refunded =\
                    rec.calculate_amount_refunded_personal_trainer_service(
                        total_amount, rec.membership_id.day_membership,
                        len(rec.attendance_ids))

    @api.model
    def calculate_amount_refunded_gym_service(
            self, total_amount, total_days, days_used):
        amount_used = (total_amount / total_days) * days_used
        amount_refunded = total_amount - amount_used
        return amount_refunded

    @api.model
    def calculate_amount_refunded_personal_trainer_service(
            self, total_amount, total_days_training, days_trained):
        amount_used = (total_amount / total_days_training) * days_trained
        amount_refunded = 0.5 * (total_amount - amount_used)
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
            'amount_refunded': self.amount_refunded,
            'current_membership_line': self.id
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

    @api.multi
    def unlink(self):
        if self.filtered(
                lambda m: m.account_invoice_id and
                m.account_invoice_id.state == 'paid'):
            raise UserError(
                _('You cannot delete membership lines which have '
                  'paid invoice!'))
        return super(MembershipLine, self).unlink()

    @api.depends('date_to')
    def _compute_is_expired(self):
        today = fields.Date.context_today(self)
        print('today', today)
        for rec in self:
            if rec.state == 'paid' and rec.date_to < today:
                rec.is_expired = True
            else:
                rec.is_expired = False

    @api.depends('account_invoice_line.invoice_id.state',
                 'account_invoice_line.invoice_id.payment_ids',
                 'invoice_refund_id.state')
    def _compute_state(self):
        """
        Override to change the way finding credit note for an invoice.
        """
        invoice_obj = self.env['account.invoice']
        for line in self:
            self._cr.execute('''
            SELECT i.state, i.id FROM
            account_invoice i
            WHERE
            i.id = (
                SELECT l.invoice_id FROM
                account_invoice_line l WHERE
                l.id = (
                    SELECT  ml.account_invoice_line FROM
                    membership_membership_line ml WHERE
                    ml.id = %s
                    )
                )
            ''', (line.id,))
            fetched = self._cr.fetchone()
            if not fetched:
                line.state = 'canceled'
                continue
            istate = fetched[0]
            if istate == 'draft':
                line.state = 'waiting'
            elif istate == 'open':
                line.state = 'invoiced'
            elif istate == 'paid':
                line.state = 'paid'
                invoice = invoice_obj.browse(fetched[1])
                if invoice:
                    refund_invoices = invoice_obj.search([
                        ('type', '=', 'out_refund'),
                        ('origin', '=', invoice.number),
                        ('state', '=', 'paid')], limit=1)
                    if refund_invoices:
                        line.state = 'canceled'
            elif istate == 'cancel':
                line.state = 'canceled'
            else:
                line.state = 'none'
