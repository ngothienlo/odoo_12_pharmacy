import base64
import imghdr
from io import BytesIO
from odoo import models, _
from itertools import groupby
import string
from odoo.modules.module import get_module_resource


class QuotationXlsxReport(models.AbstractModel):
    _name = 'report.kingsport_quotation_xlsx_report'
    _inherit = 'report.report_xlsx.abstract'
    _description = _('Quotation / Order Excel')

    def generate_xlsx_report(self, workbook, data, objects):
        # init
        self.row = 0
        self.object = objects[0]
        self._define_formats(workbook)
        self.sheet = workbook.add_worksheet(_('Report'))
        self.setup_config()

        # generate report header
        self.generate_company_information()

        # generate report content
        self.generate_content()

    def generate_company_information(self):
        company_info = self.object.env.user.company_id
        if not company_info:
            return
        # company logo
        if company_info.logo:
            image_base64 = base64.b64decode(company_info.logo)
            image_data = BytesIO(image_base64)
            filename = 'logo.' + (imghdr.what(None, h=image_base64) or 'png')
            self.sheet.merge_range('A1:I1', '')
            self.sheet.insert_image(
                'A1', filename,
                {'image_data': image_data, 'x_scale': 0.8, 'y_scale': 0.8})
        # company banner
        image_banner = get_module_resource(
            'kingsport_module', 'static/img/kingsport_banner.png')
        image_banner = open(image_banner, 'rb')
        if image_banner:
            image_data2 = BytesIO(image_banner.read())
            image_banner.close()
            self.sheet.insert_image(
                'C1', 'kingsport_banner.png',
                {'image_data': image_data2, 'x_scale': 1, 'y_scale': 0.9})
        # mark row number
        self.row = 4

    def generate_content(self):
        # generate table header
        self.sheet.merge_range(
            'A2:I2', u'Bảng Báo Giá Setup Gym KINGSPORT',
            self.format_table_name)
        self.sheet.merge_range(
            'A3:I3',
            'TẬP ĐOÀN KINGSPORT KÍNH CHÚC QUÝ KHÁCH '
            'NHIỀU SỨC KHỎE & THÀNH CÔNG!',
            self.format_header2)

        # mark row number
        self.row = 3
        # generate table header
        self.generate_table_header()
        # generate table content
        self.generate_table_content()
        # generate table footer
        self.generate_table_footer()
        # generate content footer
        self.generate_content_footer()

    def generate_image(self, image):
        if image:
            image_base64 = base64.b64decode(image)
            image_data = BytesIO(image_base64)
            filename = 'product.' + \
                (imghdr.what(None, h=image_base64) or 'png')
            self.sheet.insert_image(
                'I{0}'.format(self.row), filename,
                {'image_data': image_data, 'x_scale': 1.469, 'y_scale': 1.5})
        return True

    def generate_line_product(self, data):
        self.row += 1
        self.sheet.set_row(self.row - 1, 150)
        self.sheet.write_row(
            'A{0}'.format(self.row), data[0:2], self.format_line_product)
        self.sheet.merge_range(
            'C{0}:D{0}'.format(self.row), data[2], self.format_line_product)
        self.sheet.write_row(
            'E{0}'.format(self.row), data[3:4], self.format_line_product)
        self.sheet.write_number(
            'F{0}'.format(self.row), data[4], self.format_money)
        self.sheet.write_number(
            'G{0}'.format(self.row), data[5], self.format_uom_qty)
        self.sheet.write_formula(
            'H{0}'.format(self.row),
            'F{0}*G{0}'.format(self.row),
            self.format_money)
        self.sheet.write(
            'I{0}'.format(self.row), '', self.format_line_product)
        # insert image
        self.generate_image(data[6])

    def generate_line_categogy(self, content_tt, content_category):
        self.row += 1
        self.sheet.set_row(self.row - 1, 30)
        self.sheet.merge_range(
            'B{0}:I{0}'.format(self.row), content_category,
            self.format_line_category)
        self.sheet.write_row(
            'A{0}'.format(self.row), content_tt, self.format_line_category)

    def generate_table_header(self):
        header_name = [
            'TT',
            'Tên Sản Phẩm',
            'Thông Số Kỹ Thuật',
            'Xuất Xứ',
            'Gía Sản Phẩm',
            'Số lượng',
            'Thành Tiền',
            'Hình Ảnh',
        ]
        self.row += 1
        self.sheet.write_row('A{0}'.format(self.row), header_name[0:2],
                             self.format_table_content_header_bg_01)
        self.sheet.merge_range('C4:D4', header_name[2],
                               self.format_table_content_header_bg_01)
        self.sheet.write_row('E{0}'.format(self.row), header_name[3:8],
                             self.format_table_content_header_bg_01)

    def generate_table_content(self):
        # load content with sale order line
        cate_other = self.env.ref('kingsport_module.product_category_other')
        order_lines = self.object.order_line.filtered(
            lambda line: line.display_type not in [
                'line_section', 'line_note']) or []
        order_lines_other = order_lines.filtered(
            lambda line: line.product_id.categ_id.id == cate_other.id) or []
        order_lines = order_lines.filtered(
            lambda line: line.product_id.categ_id.id != cate_other.id) or []
        list_order_line = [
            (line, line.product_id.categ_id.name) for line in order_lines]
        list_order_line.sort(key=lambda x: x[1])
        group_cates = groupby(list_order_line, key=lambda x: x[1])
        num2alpha = dict(zip(range(1, 27), string.ascii_uppercase))
        num2alpha_num = 1
        row_temp = 1
        for (key, groups) in group_cates:
            cate_name = ''
            cate_name = 'Dòng sản phẩm {0}'.format(key)
            self.generate_line_categogy(num2alpha[num2alpha_num], cate_name)
            num2alpha_num += 1
            for item in groups:
                data = self.get_data_so_line(item[0], row_temp)
                self.generate_line_product(data)
                row_temp += 1
        if order_lines_other:
            cate_name = 'Dòng sản phẩm {0}'.format(cate_other.name or '')
            self.generate_line_categogy(num2alpha[num2alpha_num], cate_name)
            for line in order_lines_other:
                data = self.get_data_so_line(line, row_temp)
                self.generate_line_product(data)
                row_temp += 1

    def get_data_so_line(self, line, row_temp):
        data = []
        data.append(row_temp)
        str_name = '{0}\n'.format(line.product_id.display_name or '')
        data.append(str_name)
        str_info = line.product_id.product_specification or ''
        data.append(str_info)
        str_origin = line.product_id.origin or ''
        data.append(str_origin)
        data.append(line.price_unit or 0)
        data.append(line.product_uom_qty or 0)
        data.append(line.product_id.image_medium or line.product_id.image)
        return data

    def generate_table_footer(self):
        # total price + not vat
        self.generate_total_price()
        # support customer
        self.support_customer()

    def support_customer(self):
        self.row += 1
        supports = [
            'Bằng cấp huấn luyện viên',
            '10 Tấm Poster khổ chuẩn ( 60 x 80 Cm )',
            'Phần mềm quản lý Gym',
            'Thiết kế logo, bảng hiệu ( File mềm )',
            'Truyền thông 1 tháng',
        ]
        self.sheet.merge_range(
            'A{0}:E{1}'.format(self.row, self.row+4),
            u'Hỗ trợ khách hàng ', self.format_table_footer_support)
        for i in range(0, 5):
            self.sheet.set_row(self.row - 1 + i, 36)
            self.sheet.merge_range(
                'F{0}:I{0}'.format(self.row + i),
                supports[i], self.format_table_footer_support_item)
        self.row = self.row + 4
        return True

    def generate_total_price(self):
        self.row += 1
        self.sheet.set_row(self.row - 1, 45)
        self.sheet.merge_range(
            'A{0}:E{0}'.format(self.row), u'Giá trên chưa bao gồm 10% VAT',
            self.format_table_footer)
        self.sheet.write(
            'F{0}'.format(self.row), u'Tổng cộng',
            self.format_table_footer_total)
        self.sheet.write_formula(
            'G{0}'.format(self.row), '=SUM(G6:G{0})'.format(self.row-1),
            self.format_table_footer_total)
        self.sheet.write_formula(
            'H{0}'.format(self.row), '=SUM(H6:H{0})'.format(self.row-1),
            self.format_money_total)
        self.sheet.write(
            'I{0}'.format(self.row), '', self.format_table_footer)
        return True

    def generate_content_footer(self):
        self.row += 1
        self.generate_sale_order_note()
        self.generate_sale_person()
        self.generate_showroom_info()
        return True

    def generate_sale_order_note(self):
        note_and_condition = self.object.note or False
        note_service = self.object.company_id and\
            self.object.note_service or False
        note_payment_method = self.object.company_id and\
            self.object.note_payment_method or False
        note_delivery_method = self.object.company_id and\
            self.object.note_delivery_method or False
        if note_and_condition:
            self.sheet.merge_range(
                'B{0}:I{1}'.format(self.row, self.row+5),
                note_and_condition, self.format_note_category)
            self.row += 6
        if note_service:
            self.sheet.merge_range(
                'B{0}:I{0}'.format(self.row),
                '1. Dịch vụ', self.format_note_category)
            self.row += 1
            self.sheet.merge_range(
                'B{0}:I{1}'.format(self.row, self.row + 10),
                note_service, self.format_note)
            self.row += 11
        if note_payment_method:
            self.sheet.merge_range(
                'B{0}:I{0}'.format(self.row),
                '2. Hình thức thanh toán', self.format_note_category)
            self.row += 1
            self.sheet.merge_range(
                'B{0}:I{1}'.format(self.row, self.row + 6),
                note_payment_method, self.format_note)
            self.row += 7
        if note_delivery_method:
            self.sheet.merge_range(
                'B{0}:I{0}'.format(self.row),
                '3. Phương thức giao hàng', self.format_note_category)
            self.row += 1
            self.sheet.merge_range(
                'B{0}:I{1}'.format(self.row, self.row + 3),
                note_delivery_method, self.format_note)
            self.row += 4
        self.sheet.merge_range(
            'B{0}:I{0}'.format(self.row),
            '', self.format_note_category)
        return True

    def generate_sale_person(self):
        self.row += 1
        user = self.object.user_id
        name = user.name or ''
        email = user.email or ''
        phone = (user.mobile or '') + ', ' + (user.phone or '')
        hot_line = self.env['ir.config_parameter'].sudo().get_param(
            'hot_line', '')

        self.sheet.merge_range(
            'B{0}:I{0}'.format(self.row), name, self.format_name)
        self.row += 1
        self.sheet.merge_range(
            'B{0}:I{0}'.format(self.row),
            u'Số Điện thoại: ' + phone, self.format_info_sale_person)
        self.row += 1
        self.sheet.merge_range(
            'B{0}:I{0}'.format(self.row),
            u'Tổng đài tư vấn: ' + hot_line, self.format_info_sale_person)
        self.row += 1
        self.sheet.merge_range(
            'B{0}:I{0}'.format(self.row),
            u'Email: ' + email, self.format_info_sale_person)
        self.row += 1
        self.sheet.merge_range(
            'B{0}:I{0}'.format(self.row), '', self.format_info_sale_person)
        return True

    def generate_showroom_info(self):
        showroom_info = self.object.company_id and\
            self.object.company_id.showroom_info or ''
        self.row += 1
        self.sheet.merge_range(
            'B{0}:I{0}'.format(self.row),
            '', self.format_note_category)
        self.sheet.merge_range(
            'B{0}:K{1}'.format(self.row, self.row + 69),
            showroom_info, self.format_note)
        return True

    def _define_formats(self, workbook):
        # common
        format_config = {
            'font_name': 'Times New Roman',
            'font_size': 10,
            'valign': 'vcenter',
            'align': 'left',
            'text_wrap': False,
        }
        format_add_boder = ({'border': True})
        self.format_add_boder = workbook.add_format(format_add_boder)
        self.format_default = workbook.add_format(format_config)
        # Header 2
        format_header2 = {
            'font_name': 'Times New Roman',
            'font_size': 24,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': False,
            'color': '#318006',
        }
        self.format_header2 = workbook.add_format(format_header2)
        # Line category
        format_line_category = format_config.copy()
        format_line_category.update({
            'font_name': 'Times New Roman',
            'font_size': 20,
            'align': 'center',
            'text_wrap': False,
            'bg_color': '#ffce45',
            'border': 1,
            'bold': True
        })
        self.format_line_category = workbook.add_format(format_line_category)
        # Line product
        format_line_product = {
            'font_name': 'Times New Roman',
            'font_size': 18,
            'align': 'center',
            'text_wrap': True,
            'border': True,
            'valign': 'vcenter'
        }
        self.format_line_product = workbook.add_format(format_line_product)
        # Line product format sl
        format_uom_qty = format_line_product.copy()
        format_uom_qty.update({'color': 'red'})
        self.format_uom_qty = workbook.add_format(format_uom_qty)
        # Line productmoney format
        format_money = format_line_product.copy()
        format_money.update({
            'num_format': '###,###,###,##0',
            'color': 'red'
        })
        self.format_money = workbook.add_format(format_money)
        # company name
        format_company_name = format_config.copy()
        format_company_name.update({
            'font_size': 12,
            'bold': True,
        })
        self.format_company_name = workbook.add_format(format_company_name)
        # report content
        # table name
        format_table_name = format_config.copy()
        format_table_name.update({
            'font_name': 'Time New Roman',
            'font_size': 48,
            'align': 'center',
            'bold': True,
            'color': '#0566cd',
        })
        self.format_table_name = workbook.add_format(format_table_name)
        # report table_content_header
        format_table_content_header = format_config.copy()
        format_table_content_header.update({
            'border': True,
            'bold': True,
            'text_wrap': True,
            'align': 'center',
            'bg_color': '#F0997E',
        })
        self.format_table_content_header = \
            workbook.add_format(format_table_content_header)
        # report table_content_header
        format_table_content_header_bg_01 = format_config.copy()
        format_table_content_header_bg_01.update({
            'border': True,
            'bold': True,
            'text_wrap': True,
            'align': 'center',
            'font_size': 18,
        })
        self.format_table_content_header_bg_01 = \
            workbook.add_format(format_table_content_header_bg_01)
        # report table content footer
        format_table_footer = format_line_product.copy()
        format_table_footer.update({
            'font_size': 26,
            'bold': True
        })
        self.format_table_footer = \
            workbook.add_format(format_table_footer)
        # report table content footer total price
        format_table_footer_total = format_table_footer.copy()
        format_table_footer_total.update({
            'color': 'red',
            'bg_color': '#fce844',
            'size': 22
        })
        self.format_table_footer_total = \
            workbook.add_format(format_table_footer_total)
        # Line money format total
        format_money_total = format_table_footer_total.copy()
        format_money_total.update({
            'num_format': '###,###,###,###',
        })
        self.format_money_total = workbook.add_format(format_money_total)
        # report table content footer: support customer
        format_table_footer_support = format_table_footer.copy()
        format_table_footer_support.update({'size': 40})
        self.format_table_footer_support = \
            workbook.add_format(format_table_footer_support)
        # report table content footer: support customer item
        format_table_footer_support_item = format_table_footer.copy()
        format_table_footer_support_item.update({'size': 30})
        self.format_table_footer_support_item = \
            workbook.add_format(format_table_footer_support_item)
        # report table content footer: note for sale order
        format_table_footer_note = format_table_footer.copy()
        format_table_footer_note.update({
            'text_wrap': True, 'valign': 'vcenter',
            'align': 'left', 'size': 22})
        self.format_table_footer_note = \
            workbook.add_format(format_table_footer_note)
        # format name
        format_name = format_table_footer_note.copy()
        format_name.update({'size': 28, 'bold': True, 'border': 0})
        self.format_name = \
            workbook.add_format(format_name)
        # format info sale person
        format_info_sale_person = format_table_footer_note.copy()
        format_info_sale_person.update(
            {'border': 0, 'bold': False})
        self.format_info_sale_person = \
            workbook.add_format(format_info_sale_person)
        # format note
        format_note = format_table_footer_note.copy()
        format_note.update(
            {'font_size': 22, 'border': 0, 'bold': False, 'valign': 'vcenter'})
        self.format_note = workbook.add_format(format_note)
        # format note category
        format_note_category = format_table_footer_note.copy()
        format_note_category.update(
            {'border': 0})
        self.format_note_category = workbook.add_format(format_note_category)

    def setup_config(self):
        self._set_default_format()

    def _set_default_format(self):
        self.sheet.set_column('A:Z', None, self.format_default)

        self.sheet.set_row(0, 140)
        self.sheet.set_row(1, 60)
        self.sheet.set_row(2, 42)
        self.sheet.set_row(3, 30)
        self.sheet.set_row(4, 25)

        self.sheet.set_column('A:A', 5)
        self.sheet.set_column('B:B', 33)
        self.sheet.set_column('C:C', 20)
        self.sheet.set_column('D:D', 30)
        self.sheet.set_column('E:E', 13)
        self.sheet.set_column('F:F', 27)
        self.sheet.set_column('G:G', 17)
        self.sheet.set_column('H:H', 30)
        self.sheet.set_column('I:I', 26)

        self.sheet.hide_gridlines(2)
