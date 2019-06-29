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
{
    'name': 'Project Kingpsort installer',
    'version': '12.0.0.1.0',
    'category': 'Trobz Standard Modules',
    'description': """
This module will install all module dependencies of Kingpsort.
    """,
    'author': 'Trobz',
    'website': 'http://www.trobz.com',
    'depends': [

        # Trobz Addons
        'crm_required_fields_state',
        'crm_activity',
        'l10n_vn_country_state',

        # Odoo Native
        'crm',
        'sale_management',
        'purchase',
        'stock',
        'account',
        'membership',

        # OCA Addons
        'web_responsive',

        # Other Addons
        'orange_theme_odoo12'

    ],
    'data': [
        # ============================================================
        # SECURITY SETTING - GROUP - PROFILE
        # ============================================================
        # 'security/',
        'security/ir.model.access.csv',

        # ============================================================
        # DATA
        # ============================================================
        # 'data/',
        'data/ir_config_parameter.xml',
        'data/product_category.xml',
        'data/business_category.xml',
        'data/stock_location.xml',
        'data/crm_stage.xml',
        'data/product_template.xml',

        # ============================================================
        # VIEWS
        # ============================================================
        # 'view/',
        'views/base/res_partner_views.xml',

        'views/crm/crm_lead_views.xml',
        'views/crm/crm_stage_views.xml',
        'views/crm/crm_team_views.xml',
        'views/crm/crm_stage_views.xml',
        'views/crm/crm_lead_allocation_views.xml',

        'views/membership/membership_membership_line_views.xml',
        'views/membership/product_template_views.xml',
        'views/membership/res_partner_views.xml',
        'views/membership/stock_location_gym_views.xml',

        'views/sale/business_category_views.xml',
        'views/sale/product_category_views.xml',
        'views/sale/sale_order_views.xml',
        'views/sale/product_template_views.xml',
        'views/sale/sale_location_selection_views.xml',

        'views/stock/stock_picking_views.xml',
        'views/stock/product_template_views.xml',

        # ============================================================
        # WIZARD
        # ============================================================
        'wizards/membership/membership_invoice.xml',

        # ============================================================
        # MENU
        # ============================================================
        # 'menu/',
        'menu/menu.xml',
        'menu/membership_menu.xml',

        # ============================================================
        # FUNCTION USED TO UPDATE DATA LIKE POST OBJECT
        # ============================================================
        # "data/function.xml",
    ],

    'test': [],
    'demo': [],

    'installable': True,
    'active': False,
    'application': True,
}
