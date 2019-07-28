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
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    use_sale_note = fields.Boolean(default=True)
    hot_line = fields.Char()

    def get_values(self):
        """
        Read document configurations from system parameter
        """
        res = super(ResConfigSettings, self).get_values()
        IrConfig = self.env['ir.config_parameter'].sudo()
        hot_line = IrConfig.get_param('hot_line', '')
        res.update({'hot_line': str(hot_line) or ''})
        return res

    def set_values(self):
        """
        Update changing configurations to system parameter
        """
        super(ResConfigSettings, self).set_values()
        param_obj = self.env['ir.config_parameter']
        for record in self:
            param_obj.sudo().set_param('hot_line', record.hot_line)
