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
                'update_sale_note',
                'update_administrator',
                'archive_all_country_and_child_not_vn',
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
    def archive_all_country_and_child_not_vn(self):
        _logger.info(
            '========== Start archive all country and child not VN ==========')
        arch_country_ids = self.env['res.country'].search(
            [('code', '!=', 'VN')])
        arch_state_ids = self.env['res.country.state'].search(
            [('country_id', 'in', arch_country_ids.ids)])
        arch_state_ids.write({'active': False})
        arch_country_ids.write({'active': False})
        _logger.info(
            '========== Start archive all country and child not VN ==========')
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
    def update_sale_note(self):
        _logger.info('========== Start update sale note ==========')
        note_service =\
            ('\tBảo hành chính hãng 2 năm hoặc thay thế '
             'linh kiện miễn phí một lần trong 2 năm.\n\t'
             'Thiết kế theo công nghệ Mỹ.\n\t'
             'Đạt tiêu chuẩn thiết kế ở châu Âu.\n\t'
             'Có đầy đủ linh kiện thay thế cho khách hàng.\n\t'
             'Kinh nghiệm cung cấp và lắp đặt phòng tập, khách sạn, '
             'resort hơn 10 năm qua.\n\t'
             'KINGSPORT tự hào là nhà sản xuất, nhập khẩu và phân phối các '
             'dòng máy tập thể thao hàng đầu thế giới.')
        note_payment_method =\
            ('\tChuyển khoản hoặc tiền mặt\n\t'
             'Đặt cọc 50% sau khi ký hợp đồng ,  thanh toán 40% trước khi '
             'giao hàng 3 ngày , nghiệm thu sau 7 ngày thanh toán '
             '10% còn lại.\n\t'
             'Thời gian giao hàng do 2 bên tự thỏa thuận '
             '( 45 - 60 ngày kể từ ngày ký hợp đồng * Tùy sản phẩm )')
        note_delivery_method =\
            ('\tBằng xe tải hoặc gửi hàng qua nhà xe (tùy số lượng).\n\t'
             'Để biết thêm chi tiết, quý khách vui lòng liên hệ với chuyên '
             'viên tư vấn của TẬP ĐOÀN KINGSPORT')
        showroom_info =\
            ('*21 CHI NHÁNH MIỀN NAM:\n\t'
             'Chi nhánh Kingsport Bình Chánh ( Trụ sở chính ) :161 – 163 – '
             '165 Đường số 9A - KDC Trung Sơn - Bình Chánh - TP.HCM.\n\t'
             'Chi nhánh Kingsport Tân Phú: 589 Lũy Bán Bích - P Phú Thạnh - '
             'Q.Tân Phú – TPHCM.\n\t'
             'Chi nhánh Kingsport Bình Thạnh: 384 Điện Biên Phủ - P.17 - '
             'Q. Bình Thạnh – TPHCM.\n\t'
             'Chi nhánh Kingsport Gò Vấp: 509A Quang Trung P10 Gò Vấp ; '
             '901 - 903 Phan Văn Trị  P7 - Q.Gò Vấp – TPHCM.\n\t'
             'Chi nhánh Kingsport Quận 6 : 167A Nguyễn Văn Luông -P10 '
             '- Q.6 – TPHCM.\n\t'
             'Chi nhánh Kingsport Quận 5 : 566 Nguyễn Trãi -P8 - '
             'Q.5 – TPHCM.\n\t'
             'Chi nhánh Kingsport Quận Phú Nhuận : 82 Hoàng Văn Thụ -P9 '
             '- Q.Phú Nhuận – TPHCM.\n\t'
             'Chi nhánh Kingsport Quận Thủ Đức : 769 Kha Vạn Cân -P.Linh Tây '
             '- Q.Thủ Đức – TPHCM.\n\t'
             'Chi nhánh Kingsport Quận 12 : Lầu 2 Siêu thị Big C Pandora - '
             'Trường Chinh - Q12 - TPHCM.\n\t'
             'Chi nhánh Kingsport Quận Tân Bình : 1051 Cách Mạng Tháng 8 - '
             'P7 Q. Tân Bình - TPHCM.\n\t'
             'Chi nhánh Kingsport Biên Hòa – Đồng Nai: 410 Nguyễn Ái Quốc '
             '- KP.5 - P. Tân Tiến - TP. Biên Hòa – ĐồngNai.\n\t'
             'Chi nhánh Kingsport Bình Dương: 458 Đại Lộ Bình Dương '
             '- P. Hiệp Thành - TP. Thủ Dầu Một – Bình Dương.\n\t'
             'Chi nhánh Kingsport Vũng Tàu: 39 Nam Kỳ Khởi Nghĩa - P.3 - '
             'TP. Vũng Tàu.\n\t'
             'Chi nhánh Kingsport Cần Thơ: 279AA Nguyễn Văn Cừ - '
             'Q.Ninh Kiều – Cần Thơ.\n\t'
             'Chi nhánh Kingsport Long An : 122-124 Hùng Vương (nối dài), '
             'Phường 6, TP. Tân An.\n\t'
             'Chi nhánh Kingsport Tây Ninh : 954 Cách Mạng Tháng Tám, '
             'P.4, TP.Tây Ninh.\n\t'
             'Chi nhánh Kingsport Tiền Giang : 163 Nguyễn Thị Thập - P5 '
             '-Tp Mỹ Tho ..\n\t'
             'Chi nhánh Kingsport Kiên Giang : LôD5 29-30 Đường 3.2  '
             '- P Vĩnh Lạc – Tp Rạch Giá.\n\t'
             'Chi nhánh Kingsport An Giang : 152/5 Trần Hưng Đạo - '
             'P Mỹ Phước – Long Xuyên - An Giang.\n\t'
             'Chi nhánh Kingsport Bạc Liêu : 132/4 Trần Phú '
             '( Quốc Lộ 1A cũ ) P7 - Tp Bạc Liêu ..\n\t'
             'Chi nhánh Kingsport Cần Thơ: 279AA Nguyễn Văn Cừ - '
             'Q.Ninh Kiều – Cần Thơ.\n'
             '*9 CHI NHÁNH MIỀN TRUNG & TÂY NGUYÊN:.\n\t'
             'Chi nhánh Kingsport Đà Nẵng: 280 Đống Đa - P Thanh Bình - '
             'Hải Châu - TP. Đà Nẵng.\n\t'
             'Chi nhánh Kingsport Nghệ An : 263 Phong Định Cảng, Tp. Vinh.\n\t'
             'Chi nhánh Kingsport Huế : Tòa nhà Văn Phòng, ĐS 7, KĐT mới '
             'An Cựu, P. An Đông, Tp. Huế.\n\t'
             'Chi nhánh Kingsport Đà Lạt : 158 Hai Bà Trưng, Phường 6, '
             'Tp. Đà Lạt.\n\t'
             'Chi nhánh Kingsport Quảng Ngãi : 200 Hùng Vương, P. Trần Phú, '
             'Tp. Quảng Ngãi.\n\t.'
             'Chi nhánh Kingsport Bình Định : 424 Tây Sơn, P. Quang Trung, '
             'Tp. Quy Nhơn.\n\t'
             'Chi nhánh Kingsport Nha Trang : 32 Cửu Long, P. Phước Hòa, '
             'TP. Nha Trang.\n\t'
             'Chi nhánh Kingsport Gia Lai : 77 Trường Chinh, phường Trà Bá, '
             'Thành phố Pleiku.\n\t'
             'Chi nhánh Kingsport Đắk Lắk : C3-C5 Nguyễn Đình Chiểu, '
             'P. Tân Lợi, TP. Buôn Ma Thuột.\n'
             '*11 CHI NHÁNH MIỀN BẮC:.\n\t'
             'Chi nhánh Kingsport Quận Cầu Giấy: 96 Nguyễn Đình Hoàn - '
             'P.Nghĩ Đô - Q.Cầu Giấy – Hà Nội.\n\t'
             'Chi nhánh Kingsport Quận Hà Đông : Lô E9 - E10 Tỉnh Lộ 70, '
             'Q. Thanh Trì (Ngã 3 Yên Xá).\n\t'
             'Chi nhánh Kingsport Quận Long Biên: 59 phố Việt Hưng - '
             'P. Việt Hưng - Q. Long Biên – Hà Nội.\n\t'
             'Chi nhánh Kingsport Quận Tây Hồ : 145 Âu Cơ, P. Tứ Liên, '
             'Q. Tây Hồ.\n\t'
             'Chi nhánh Kingsport Quận Bắc Từ Liêm : 86-88 Phố Nhổn, '
             'P. Tây Tựu, Q. Bắc Từ Liêm.\n\t'
             'Chi nhánh Kingsport Hải Phòng : 510 Nguyễn Văn Linh, '
             'Q. Lê Chân, Tp. Hải Phòng.\n\t'
             'Chi nhánh Kingsport Hưng Yên : 57 phố Chùa Chuông, '
             'P. Hiến Nam, Tp. Hưng Yên.\n\t'
             'Chi nhánh Kingsport Quảng Ninh : 624 Hạ Long, P. Bãi Cháy, '
             'TP. Hạ Long, Quảng Ninh.\n\t'
             'Chi nhánh Kingsport Hải Phòng : 510 Nguyễn Văn Linh, '
             'Q. Lê Chân, Tp. Hải Phòng.\n\t'
             'Chi nhánh Kingsport Thanh Hóa : 789A Nguyễn Trãi, '
             'P. Phú Sơn, Tp. Thanh Hóa')
        self.env.ref('base.main_company').write({'note_service': note_service})
        self.env.ref('base.main_company').write(
            {'note_payment_method': note_payment_method})
        self.env.ref('base.main_company').write(
            {'note_delivery_method': note_delivery_method})
        self.env.ref('base.main_company').write(
            {'showroom_info': showroom_info})
        _logger.info('========== End update sale note ==========')
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
            'show_operations': False
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
            'group_stock_adv_location': True,
            'group_discount_per_so_line': True,
            'multi_sales_price': True,
            'group_sale_delivery_address': True,
            'po_order_approval': True,
            'po_double_validation_amount': 0,
            'multi_sales_price_method': 'formula',
            'sale_pricelist_setting': 'formula'
            # 'theme_color_brand': '#eb7979',
            # 'theme_color_primary': '#ff5252',
            # 'theme_color_required': '#f5c5c5',
            # 'theme_color_appbar_color': '#EBEDF1'
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

    @api.model
    def update_administrator(self):
        _logger.info('========== Start Update Administrator ==========')
        self.env.ref('base.user_admin').write({
            'sidebar_type': 'invisible',
            'chatter_position': 'sided'
        })
        _logger.info('========== End Update Administrator ==========')
        return True
