from odoo import models, fields, api

class CreatePlannedLines(models.TransientModel):
    _name = 'create.planned.lines'
    _description = 'Create Planned Lines Wizard'

    plan_id = fields.Many2one('purchase.order.plan', required=True, readonly=True)
    round_name = fields.Char(required=True)
    vendor_id = fields.Many2one('res.partner', string='Vendor', domain=[('supplier_rank', '>', 0)], required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    exchange_rate = fields.Float(string='Exchange Rate', default=1.0)
    container_qty = fields.Integer(string='Number of Containers')
    scheduled_date = fields.Date()
    product_line_ids = fields.One2many('create.planned.lines.product', 'wizard_id', string='Products')

    def action_create(self):
        plan_line = self.env['purchase.order.plan.line'].create({
            'plan_id': self.plan_id.id,
            'round_name': self.round_name,
            'vendor_id': self.vendor_id.id,
            'container_qty': self.container_qty,
            'scheduled_date': self.scheduled_date,
        })
        for p in self.product_line_ids:
            self.env['purchase.order.plan.line.product'].create({
                'plan_line_id': plan_line.id,
                'product_id': p.product_id.id,
                'product_qty': p.product_qty,
                'price_unit': p.price_unit,
            })
        
        self.plan_id.action_schedule()
        
        return {
            'name': 'Convert to PO',
            'type': 'ir.actions.act_window',
            'res_model': 'convert.to.po',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_plan_line_id': plan_line.id},
        }

