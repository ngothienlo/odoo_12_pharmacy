from odoo import fields, models


class StockLocationGym(models.Model):
    _name = "stock.location.gym"

    name = fields.Char('Name', required=True)
    showroom_id = fields.Many2one(
        'stock.location', string='Showroom',
        domain=[('usage', '=', 'internal')])
