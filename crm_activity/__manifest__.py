# Copyright 2009-2019 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'CRM Activity',
    'version': '1.0',
    'category': 'Trobz Standard Modules',
    'description': """
This module will install all module dependencies of dfurni.
    """,
    'author': 'Trobz',
    'website': 'http://www.trobz.com',
    'depends': [
        'crm',
        'sales_team',
        'sale',
    ],
    'data': [
        # ============================================================
        # SECURITY SETTING - GROUP - PROFILE
        # ============================================================
        # 'security/',
        'security/ir.model.access.csv',
        # 'security/post_object_security.xml',
        # ============================================================
        # DATA
        # ============================================================
        # 'data/',
        'data/activity_result_data.xml',
        'data/activity_followup_data.xml',
        # 'data/mail_activity_type_data.xml',
        # ============================================================
        # VIEWS
        # ============================================================
        # 'view/',
        'view/crm/activity_result_view.xml',
        'view/crm/activity_followup_view.xml',
        'view/crm/mail_activity_view.xml',
        'view/crm/crm_lead_view.xml',
        'view/crm/activity_history_view.xml',
        'view/crm/mail_activity_type_view.xml',
        'view/templates.xml',
        # ============================================================
        # MENU
        # ============================================================
        # 'menu/',
        'menu/menu.xml',
        # ============================================================
        # FUNCTION USED TO UPDATE DATA LIKE POST OBJECT
        # ============================================================
        # "data/dfurni_update_functions_data.xml",
    ],

    'test': [],
    'demo': [],

    'installable': True,
    'active': False,
    'application': True,
}
