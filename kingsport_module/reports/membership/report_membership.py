##############################################################################
#
#    Copyright 2009-2019 Trobz (<http://trobz.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import api, models, fields, tools
from odoo.addons.kingsport_module.models.sale.\
    product_template import TYPE_MEMBERSHIP  # @UnresolvedImport
from addons.membership.models.membership import STATE


class ReportMembership(models.Model):
    _inherit = 'report.membership'

    type_membership = fields.Selection(
        selection=TYPE_MEMBERSHIP, string='Type of Membership', readonly=True)
    personal_trainer_id = fields.Many2one(
        'res.users', string='Personal Trainer', readonly=True)
    gym_location_id = fields.Many2one(
        'stock.location.gym', string='Gym', readonly=True)
    showroom_id = fields.Many2one(
        'stock.location', string='Showroom', readonly=True)
    membership_line_state = fields.Selection(
        selection=STATE, string='Membership Line State', readonly=True)

    @api.model_cr
    def init(self):
        '''Create the view'''
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
        CREATE OR REPLACE VIEW %s AS (
        SELECT
            MIN(id) AS id,
            partner_id,
            count(membership_id) as quantity,
            user_id,
            membership_state,
            associate_member_id,
            membership_amount,
            date_to,
            start_date,
            COUNT(num_waiting) AS num_waiting,
            COUNT(num_invoiced) AS num_invoiced,
            COUNT(num_paid) AS num_paid,
            SUM(tot_pending) AS tot_pending,
            SUM(tot_earned) AS tot_earned,
            membership_id,
            type_membership,
            company_id,
            personal_trainer_id,
            showroom_id,
            gym_location_id,
            membership_line_state
        FROM
            (SELECT
                MIN(p.id) AS id,
                p.id AS partner_id,
                ml.user_id AS user_id,
                p.membership_state AS membership_state,
                p.associate_member AS associate_member_id,
                p.membership_amount AS membership_amount,
                p.membership_stop AS date_to,
                p.membership_start AS start_date,
                CASE WHEN ml.state = 'waiting'  THEN ml.id END AS num_waiting,
                CASE WHEN ml.state = 'invoiced' THEN ml.id END AS num_invoiced,
                CASE WHEN ml.state = 'paid'     THEN ml.id END AS num_paid,
                CASE WHEN ml.state IN ('waiting', 'invoiced')
                    THEN SUM(il.price_subtotal) ELSE 0 END AS tot_pending,
                CASE WHEN ml.state = 'paid' OR p.membership_state = 'old'
                    THEN SUM(il.price_subtotal) ELSE 0 END AS tot_earned,
                ml.membership_id AS membership_id,
                tmpl.type_membership AS type_membership,
                p.company_id AS company_id,
                ml.personal_trainer_id AS personal_trainer_id,
                location.id AS showroom_id,
                gym.id AS gym_location_id,
                ml.state AS membership_line_state
                FROM res_partner p
                LEFT JOIN membership_membership_line ml ON (ml.partner = p.id)
                LEFT JOIN account_invoice_line il
                    ON (ml.account_invoice_line = il.id)
                LEFT JOIN account_invoice ai ON (il.invoice_id = ai.id)
                LEFT JOIN product_product product
                    ON (ml.membership_id = product.id)
                LEFT JOIN product_template tmpl
                    ON (product.product_tmpl_id = tmpl.id)
                LEFT JOIN stock_location location
                    ON (location.id = ml.showroom_id)
                LEFT JOIN stock_location_gym gym
                    ON (gym.id = ml.gym_location_id)
             WHERE p.membership_state != 'none' and p.active = 'true'
             GROUP BY
                  p.id,
                  ml.user_id,
                  p.membership_state,
                  p.associate_member,
                  p.membership_amount,
                  p.membership_start,
                  ml.membership_id,
                  p.company_id,
                  ml.state,
                  ml.id,
                  tmpl.type_membership,
                  ml.personal_trainer_id,
                  location.id,
                  gym.id,
                  ml.state
            ) AS foo
        GROUP BY
            start_date,
            date_to,
            partner_id,
            user_id,
            membership_id,
            company_id,
            membership_state,
            associate_member_id,
            membership_amount,
            type_membership,
            personal_trainer_id,
            showroom_id,
            gym_location_id,
            membership_line_state
        )""" % (self._table,))
