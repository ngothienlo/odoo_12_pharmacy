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
import logging
import base64
from odoo import models, api
from odoo.modules.module import get_module_resource

_logger = logging.getLogger(__name__)


class PostObjectDataKingsportModule(models.TransientModel):

    _name = 'post.object.data.kingsport.module'
    _description = "Technical: kingsport_module : Post Object"

    @api.model
    def start(self):
        self.env['trobz.base'].run_post_object_one_time(
            'post.object.data.kingsport.module', [
                'load_language',
                'update_locale_for_users',
                'update_main_partner',
                'update_main_company',
                'update_show_detailed_operations',
                'update_translation_product_category',
                'update_res_country_state_master_data',
                'update_address_format_for_vn',
                'add_mandatory_fields_for_lead_stage',
            ])
        self.configure_settings()
        return True

    @api.model
    def add_mandatory_fields_for_lead_stage(self):
        _logger.info(
            '========== Start add mandatory fields for lead stage ==========')
        lead_model_id = self.env['ir.model'].search(
            [('model', '=', 'crm.lead')])
        add_field_id = self.env['ir.model.fields'].search(
            [('name', 'in', ['country_id', 'state_id']),
             ('model_id', '=', lead_model_id.id)])
        self.env.ref('kingsport_module.input_lead_info').sudo().write({
            'mandatory_fields': [(6, 0, add_field_id.ids)]
        })
        _logger.info(
            '========== End add mandatory fields for lead stage ==========')
        return True

    @api.model
    def update_translation_product_category(self):
        _logger.info(
            '========== Start update translation product category ==========')
        self.env.ref('product.product_category_all').write({
            'name': u'Tất cả',
        })
        _logger.info(
            '========== End update translation product category ==========')
        return True

    @api.model
    def update_res_country_state_master_data(self):
        _logger.info(
            '========== Start update res country data ==========')
        (
            self.env.ref('l10n_vn_country_state.res_country_state_79') +
            self.env.ref('l10n_vn_country_state.res_country_state_01')
        ).write({'is_main_city': True})
        _logger.info(
            '========== End update res country data ==========')
        return True

    @api.model
    def load_language(self):
        _logger.info('========== Start Load Language ==========')
        langs_to_load = 'vi_VN'
        self.env['ir.config_parameter'].set_param('language_to_load',
                                                  langs_to_load)
        self.env['trobz.base'].load_language()
        _logger.info('========== End Load Language ==========')
        return True

    @api.model
    def update_locale_for_users(self):
        _logger.info('========== Start Update Locale For Users ==========')
        users = self.env['res.users'].search([])
        users.write({
            'lang': 'vi_VN',
            'tz': 'Asia/Ho_Chi_Minh'
        })
        _logger.info('========== End Update Locale For Users ==========')
        return True

    @api.model
    def update_show_detailed_operations(self):
        _logger.info('====== Start Update Show Detailed Operations =======')
        sp_types = self.env['stock.picking.type'].search([])
        sp_types.write({
            'show_operations': True
        })
        _logger.info('==== End Update Show Detailed Operations =====')
        return True

    @api.model
    def configure_settings(self):
        """
        Setup the configuration of all modules
        """
        _logger.info("====== START: Configure the Application =======")
        config_datas = {
            'group_use_lead': True,
            'group_product_variant': True,
            'group_stock_multi_locations': True,
            'group_discount_per_so_line': True,
            'multi_sales_price': True,
            'group_sale_delivery_address': True,
            'po_order_approval': True,
            'po_double_validation_amount': 0,
            'theme_color_brand': '#eb7979',
            'theme_color_primary': '#ff5252',
            'theme_color_required': '#f5c5c5',
            'theme_color_appbar_color': '#EBEDF1'
        }
        config_rec = self.env['res.config.settings'].create(config_datas)
        config_rec.execute()
        _logger.info("====== END: Configure the Application =======")
        return True

    @api.model
    def update_main_partner(self):
        _logger.info('========== Start Update Main Partner Data ==========')
        self.env.ref('base.main_partner').write({
            'name': u'Tập đoàn thể thao Kingsport',
            'customer': False,
            'supplier': False,
            'phone': '',
            'street': '',
            'city': '',
            'state_id': False,
            'zip': '',
            'lang': 'vi_VN',
            'website': 'https://www.kingsport.vn',
            'email': 'kingsport.vn@gmail.com',
            'country_id': self.env.ref('base.vn').id
        })
        _logger.info('========== End Update Main Partner Data ==========')
        return True

    @api.model
    def update_main_company(self):
        _logger.info('========== Start Update Main Company Data ==========')
        path = get_module_resource(
            'kingsport_module', 'static/img/theme_background.jpg')
        with open(path, 'rb') as fn:
            content = base64.encodestring(fn.read())
        self.env.ref('base.main_company').write({
            'name': u'Tập đoàn thể thao Kingsport',
            # 'currency_id': self.env.ref('base.VND').id,
            'background_image': content,
            'default_sidebar_preference': 'invisible',
            'default_chatter_preference': 'sided'
        })
        self.env['trobz.base'].update_company_logo()
        _logger.info('========== End Update Main Company Data ==========')
        return True

    @api.model
    def update_address_format_for_vn(self):
        _logger.info('======== Start Update Address Format Vietnam ========')
        self.env.ref('base.vn').write({
            'address_format': "%(street)s\n%(street2)s\n%(ward_name)s "
            "%(district_name)s\n%(state_name)s %(country_name)s",
        })
        _logger.info('======== End Update Address Format Vietnam ========')
        return True
