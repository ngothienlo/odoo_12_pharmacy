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
from odoo import models, api
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
            ])
        self.configure_settings()
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
            'po_double_validation_amount': 0
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
        self.env.ref('base.main_company').write({
            'name': u'Tập đoàn thể thao Kingsport',
            # 'currency_id': self.env.ref('base.VND').id,
        })
        self.env['trobz.base'].update_company_logo()
        _logger.info('========== End Update Main Company Data ==========')
        return True
