from odoo import models, fields,api

class PurchaseOrderPlanLineProduct(models.Model):
    _name = 'purchase.order.plan.line.product'
    _description = 'Planned Line Products'
   
    plan_line_id = fields.Many2one('purchase.order.plan.line', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_qty = fields.Float(string='Quantity', default=1.0)
    price_unit = fields.Float(string='Unit Price')
    line_amount = fields.Monetary(string='Line Amount', compute='_compute_line_amount')
    currency_id = fields.Many2one('res.currency', related='plan_line_id.plan_id.company_id.currency_id', readonly=True)

    @api.depends('product_qty', 'price_unit')
    def _compute_line_amount(self):
        for rec in self:
            rec.line_amount = rec.product_qty * rec.price_unit