# -*- coding: utf-8 -*-
{
    'name': "sol_purchase",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase_request', 'purchase', 'stock', 'purchase_stock','sol_bb_product', 'product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/pattern_security.xml',
        'views/purchase_request_views.xml',
        'views/purchase_order_views.xml',
        'report/report_action.xml',
        'report/report_sample_development.xml',
        'report/report_pattern.xml',
        'report/report_action_landscape.xml',
        'report/report_production_order.xml',
        'report/report_sample_po.xml',
        'report/report_production_po.xml',
        'report/report_production_order_tb.xml',
        'views/data_master_story.xml',
        'views/original_sample.xml',
        'views/product_menuitem.xml',
        'security/record_rule.xml',
        # 'views/templates.xml',
        'views/sequence_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
