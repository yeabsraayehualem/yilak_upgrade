from odoo import models, fields
class CreatePlannedLinesProduct(models.TransientModel):
    _name = 'create.planned.lines.product'
    _description = 'Wizard Product Line'

    wizard_id = fields.Many2one('create.planned.lines', ondelete='cascade')
    product_id = fields.Many2one('product.product', required=True)
    product_qty = fields.Float(default=1.0)
    price_unit = fields.Float()