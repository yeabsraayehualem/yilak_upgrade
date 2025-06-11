from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        selection_add=[
            ('waiting_approval', "Waiting for Approval"),
            ('approved', "Approved"),
        ],
        ondelete={'waiting_approval': 'set default', 'approved': 'set default'}
    )