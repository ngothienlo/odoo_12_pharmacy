# Copyright 2009-2019 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models, api, _
from odoo.exceptions import Warning


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def create(self, vals):
        res = super(CrmLead, self).create(vals)
        required_fields = res.check_require_boolean_field(vals)
        if required_fields:
            raise Warning(
                _("The following fields are required: %s") %
                ", ".join(map(str, required_fields)))
        return res

    @api.multi
    def write(self, vals):
        res = super(CrmLead, self).write(vals)
        for record in self:
            required_fields = record.check_require_boolean_field(vals)
            if required_fields:
                raise Warning(
                    _("The following fields are required: %s") %
                    ", ".join(map(str, required_fields)))
        return res

    def check_require_boolean_field(self, vals):
        self.ensure_one()
        missing_fields = []
        if vals.get('stage_id', False):
            stage = self.env['crm.stage'].browse(vals['stage_id'])
        else:
            stage = self.stage_id
        required_fields = stage.mandatory_fields
        for field in required_fields:
            if not self[field.name]:
                missing_fields.append(field.field_description)
        return missing_fields

    @api.multi
    def _create_lead_partner_data(self, name, is_company, parent_id=False):
        vals = super(CrmLead, self)._create_lead_partner_data(
            name, is_company, parent_id=False)
        source_name = self.source_id and self.source_id.name or ''
        vals.update({
            'birthday': self.birthday or False,
            'gender': self.gender or False,
            'source': source_name
        })
        return vals
