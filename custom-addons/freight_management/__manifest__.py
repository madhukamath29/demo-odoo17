# -*- coding: utf-8 -*-
{
    'name': "Freight Management",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.2',

    # any module necessary for this one to work correctly
    'depends': ['uom'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/freight_consignment_views.xml',
        'views/freight_consignment_order_views.xml',
        'views/views.xml',
        'views/templates.xml',
        'wizards/order_selection_wizard_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

