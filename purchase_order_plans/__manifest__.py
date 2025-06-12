{
    "name": "Purchase Order Plans",
    "version": "1.0.0",
    "author": "Your Company",
    "category": "Purchases",
    "license": "LGPL-3",
    "depends": ["purchase", "stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/create_planned_lines_views.xml",
        "views/purchase_order_plan_views.xml",
        
    ],
    "installable": True,
    "application": False,
}