from odoo import models, fields, api

class CreatePlannedLinesProduct(models.Model):
    _name = 'create.planned.lines.product'
    _description = 'Products for Create Planned Lines Wizard'

    wizard_id = fields.Many2one(
        'create.planned.lines', ondelete='cascade', required=True
    )
    product_id = fields.Many2one(
        'product.product', string="Product", required=True
    )
    
    product_qty = fields.Float(string="Quantity", required=True)
    price_unit = fields.Monetary(
        string="Unit Price", required=True,
        currency_field='currency_id'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        related='wizard_id.currency_id',
        readonly=True
    )
    line_amount = fields.Monetary(
        string="Line Amount",
        compute='_compute_line_amount',
        currency_field='currency_id',
        readonly=True
    )

    @api.depends('product_qty', 'price_unit')
    def _compute_line_amount(self):
        for rec in self:
            rec.line_amount = rec.product_qty * rec.price_unit
    @api.constrains('product_qty', 'price_unit')
    def _check_positive_values(self):
        for rec in self:
            if rec.product_qty < 0:
              raise ValidationError("Product quantity cannot be negative")
            if rec.price_unit < 0:
              raise ValidationError("Unit price cannot be negative")
    @api.constrains('product_id')
    def _check_active_product(self):
        for rec in self:
            if not rec.product_id.active:
                raise ValidationError("You cannot select an archived product")
