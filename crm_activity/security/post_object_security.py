# Copyright 2009-2019 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from odoo import models, api

_logger = logging.getLogger(__name__)

g_base_user = 'User types / Internal User'
g_sale_user = 'Sales / User: Own Documents Only'
g_sale_manager = 'Sales / Manager'


class PostObjectSecurityCrmActivityModule(models.TransientModel):
    _name = "post.object.security.crm.activity.module"
    _description = "Set up the Groups, Profiles and Access Rights"

    @api.model
    def start(self):
        _logger.info(">> START post.object.security.dfurni.activity.result <<")
        self.create_model_access_rights()
        _logger.info(">>> END post.object.security.dfurni.activity.result <<<")
        return True

    @api.model
    def create_model_access_rights(self):
        MODEL_ACCESS_RIGHTS = {
            # [1,1,1,1]: present 4 permissions:
            # "perm_read","perm_write", "perm_create","perm_unlink"
            (
                'activity.result',
                # 'activity.followup',
                'activity.history',
                'activity.type.possible.result'
            ): {
                (g_base_user,): [1, 0, 0, 0],
                (g_sale_user,): [1, 0, 0, 0],
                (g_sale_manager,): [1, 1, 1, 1],
            }
        }
        self.env['access.right.generator'].\
            with_context({'module_name': 'crm_activity'}).\
            create_model_access_rights(MODEL_ACCESS_RIGHTS)
        return True
