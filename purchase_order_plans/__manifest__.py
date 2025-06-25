{
    "name": "Purchase Order Plans",
    "version": "17.0.1.0.1",
    "author": "Your Company",
    "category": "Purchases",
    "license": "LGPL-3",
    "depends": ["base","purchase", "stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/create_planned_lines_views.xml",
        "views/purchase_order_plan_views.xml",
        "views/convert_to_po_views.xml",      
    ],
    'assets': {},
    "installable": True,
    "application": False,
}