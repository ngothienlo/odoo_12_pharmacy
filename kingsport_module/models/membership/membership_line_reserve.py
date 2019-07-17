from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

MIN_RESERVE_DAYS = 5
MAX_RESERVE_DAYS = 30*6


class MembershipLineReserve(models.Model):
    _name = "membership.line.reserve"
    _order = 'date_from, date_to'

    date_from = fields.Date(
        'Date From', required=True)
    date_to = fields.Date(
        'Date To', required=True)
    note = fields.Text('Note')
    membership_line_id = fields.Many2one(
        'membership.membership_line', string='Membership Line',
        ondelete='cascade')

    @api.multi
    def total_reserve_days(self):
        dates_reserve = 0
        for reserve in self:
            date_to = fields.Date.from_string(reserve.date_to)
            date_from = fields.Date.from_string(reserve.date_from)
            dates_reserve += (date_to - date_from).days + 1
        return dates_reserve

    @api.constrains('date_from', 'date_to', 'membership_line_id')
    def _check_dates(self):
        '''
        - Number of reserve days should be greater than
        or equal MIN_RESERVE_DAYS
        - Check Date From
        - Check interleaving between reserves.
            There are 3 cases to consider:

            s1   s2   e1   e2
            (    [----)----]

            s2   s1   e2   e1
            [----(----]    )

            s1   s2   e2   e1
            (    [----]    )
        '''
        for rec in self:
            rec._check_dates_validity(
                rec.date_from, rec.date_to, rec.membership_line_id)

            domain = [
                ('id', '!=', rec.id),
                ('membership_line_id', '=', rec.membership_line_id.id),
                '|', '|',
                '&', ('date_from', '<=', rec.date_from),
                     ('date_to', '>=', rec.date_from),
                '&', ('date_from', '<=', rec.date_to),
                     ('date_to', '>=', rec.date_to),
                '&', ('date_from', '<=', rec.date_from),
                     ('date_to', '>=', rec.date_to),
            ]

            if self.search_count(domain) > 0:
                raise ValidationError(
                    _('You can not have an overlap between two reserves, '
                      'please correct the start and/or end dates of your '
                      'reserves.'))

    @api.onchange('date_from', 'date_to', 'membership_line_id')
    def _onchange_dates(self):
        self._check_dates_validity(
            self.date_from, self.date_to, self.membership_line_id)

    @api.model
    def _check_dates_validity(self, date_from_str, date_to_str,
                              membership_line):
        if date_from_str and membership_line and membership_line.date_from and\
                date_from_str < membership_line.date_from:
            raise ValidationError(
                _('Date From of this reserve should not less than '
                  'Date From of its Membership Line!'))

        if date_from_str and date_to_str:
            date_from = fields.Date.from_string(self.date_from)
            date_to = fields.Date.from_string(self.date_to)
            if (date_to - date_from).days < MIN_RESERVE_DAYS:
                raise ValidationError(
                    _('The minimum number of reservation days is '
                      '%d day(s)!' % MIN_RESERVE_DAYS))
