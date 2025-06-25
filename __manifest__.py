{
    'name': 'Custom Sale Approval and Voiding',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Add approval and voiding features to Sales module in Odoo 17',
    'depends': ['sale_management', 'account'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
