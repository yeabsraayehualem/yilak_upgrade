from odoo import models, fields

class PurchaseOrderPlanLine(models.Model):
    _name = 'purchase.order.plan.line'
    _description = 'Planned Order Line'

    plan_id = fields.Many2one('purchase.order.plan', ondelete='cascade')
    round_name = fields.Char(required=True)
    vendor_id = fields.Many2one('res.partner', string='Vendor', domain=[('supplier_rank', '>', 0)])
    container_qty = fields.Integer(string='Number of Containers')
    scheduled_date = fields.Date()
    product_line_ids = fields.One2many('purchase.order.plan.line.product', 'plan_line_id', string='Products')