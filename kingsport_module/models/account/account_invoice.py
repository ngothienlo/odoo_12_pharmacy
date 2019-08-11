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
        '''
        Override to:
            - Update date_from for related membership_line
            - Or, update date_cancel for related membership_line
        '''
        res = super(AccountInvoice, self).write(vals)
        membership_line_obj = self.env['membership.membership_line']
        if vals.get('state', '') == 'paid':
            for rec in self:
                if rec.type in ['out_invoice', 'out_refund']:
                    # Payments is already sorted by payment_date
                    payment_date = rec.payment_ids and \
                        rec.payment_ids[0].payment_date or \
                        fields.Date.context_today(self)

                    if rec.type == 'out_invoice':
                        membership_line_obj.search([
                            ('account_invoice_line', 'in', rec.mapped(
                                'invoice_line_ids').ids)
                        ]).write({'date_from': payment_date})

                    elif rec.type == 'out_refund':
                        origin = self.search([
                            ('type', '=', 'out_invoice'),
                            ('number', '=', rec.origin)
                        ])
                        if not origin:
                            continue
                        membership_line_obj.search([
                            ('account_invoice_line', 'in',
                             origin.mapped('invoice_line_ids').ids)
                        ]).write({'date_cancel': payment_date})
        return res

    @api.multi
    @api.returns('self')
    def refund(self, date_invoice=None, date=None,
               description=None, journal_id=None):
        """
        Override to update credit note for membership_line
        """
        new_invoices = super(AccountInvoice, self).refund(
            date_invoice, date, description, journal_id)
        if new_invoices and \
                self._context.get('refund_from_membership_line_form', False):
            current_membership_line_id = self._context.get(
                'current_membership_line', False)
            current_membership_line = self.env['membership.membership_line'].\
                browse(current_membership_line_id)
            current_membership_line.write(
                {'invoice_refund_id': new_invoices[0].id})
        return new_invoices
