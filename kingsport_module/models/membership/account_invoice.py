from odoo import api, models, fields
from addons.account.models.account_invoice import MAGIC_COLUMNS


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def _refund_cleanup_lines(self, lines):
        """
        Override to update amount refunded if user using Refund feature
        from Membership
        """
        result = []
        for line in lines:
            values = {}
            for name, field in line._fields.items():
                if name in MAGIC_COLUMNS:
                    continue
                elif field.type == 'many2one':
                    values[name] = line[name].id
                elif field.type not in ['many2many', 'one2many']:
                    values[name] = line[name]
                elif name == 'invoice_line_tax_ids':
                    values[name] = [(6, 0, line[name].ids)]
                elif name == 'analytic_tag_ids':
                    values[name] = [(6, 0, line[name].ids)]
            if self._context.get('refund_from_membership_line_form', False):
                if line._name == 'account.invoice.line' and \
                        line.id == self._context.get(
                            'account_invoice_line', 0):
                    values.update(
                        {'price_unit': self._context.get('amount_refunded')})
            result.append((0, 0, values))
        return result

    @api.multi
    def write(self, vals):
        '''Update date_from for related membership_line'''
        res = super(AccountInvoice, self).write(vals)
        if vals.get('state', '') == 'paid':
            for rec in self:
                # Payments is already sorted by payment_date
                date_from = rec.payment_ids and \
                    rec.payment_ids[0].payment_date or \
                    fields.Date.context_today()
                self.env['membership.membership_line'].search([
                    ('account_invoice_line', 'in', rec.mapped(
                        'invoice_line_ids').ids)
                ]).write({'date_from': date_from})
        return res
