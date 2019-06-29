# Copyright 2009-2019 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "CRM required fields state",
    "summary": "CRM required fields state",
    "version": "12.0.1.0.0",
    "category": "CRM",
    "website": "https://trobz.com",
    "author": "Trobz ",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'crm',
    ],
    "data": [
        # data

        # view
        'views/crm_stage_view.xml'

        # security
    ],
    'installable': True,
}
