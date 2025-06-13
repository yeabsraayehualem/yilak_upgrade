from odoo import models, fields

class ConvertToPO(models.TransientModel):
    _name = 'convert.to.po'
    _description = 'Convert to Purchase Order Wizard'

    plan_line_id = fields.Many2one('purchase.order.plan.line', readonly=True)
    proforma_number = fields.Char(string='Proforma Number')
    invoice_file = fields.Binary(string='Proforma Invoice')

    def action_confirm(self):
        plan_line = self.plan_line_id
        
        po = self.env['purchase.order'].create({
            'partner_id': plan_line.vendor_id.id,
            'date_planned': plan_line.scheduled_date,
            'company_id': plan_line.plan_id.company_id.id,
            'origin': plan_line.plan_id.name,
        })
        for pl in plan_line.product_line_ids:
            self.env['purchase.order.line'].create({
                'order_id': po.id,
                'product_id': pl.product_id.id,
                'name': pl.product_id.display_name,
                'product_qty': pl.product_qty,
                'price_unit': pl.price_unit,
                'date_planned': plan_line.scheduled_date,
                'product_uom': pl.product_id.uom_id.id,
            })
       
        plan_line.plan_id.action_done()
        return {'type': 'ir.actions.act_window_close'}