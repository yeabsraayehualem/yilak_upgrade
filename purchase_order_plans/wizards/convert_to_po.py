from odoo import models, fields, api
class ConvertToPO(models.TransientModel):
    _name = 'convert.to.po'
    _description = 'Convert to Purchase Order Wizard'

    # REMOVE the ondelete parameter completely
    plan_line_id = fields.Many2one('purchase.order.plan.line', readonly=True)
    proforma_number = fields.Char(string='Proforma Number', required=True)
    invoice_file = fields.Binary(string='Proforma Invoice',required=True)

    def action_confirm(self):
        _logger.info("=== STARTING ACTION_CONFIRM ===")
        _logger.info(f"Plan line ID: {self.plan_line_id.id}")
        _logger.info(f"Plan line exists: {bool(self.plan_line_id.exists())}")
        self.ensure_one()
        if not self.plan_line_id:
            raise ValidationError("No plan line selected for conversion")
        
        plan_line = self.plan_line_id

        # Create the purchase order
        po = self.env['purchase.order'].create({
            'partner_id': plan_line.vendor_id.id,
            'date_planned': plan_line.scheduled_date,
            'company_id': plan_line.plan_id.company_id.id,
            'origin': f"{plan_line.plan_id.name} - {self.proforma_number}",
        })
        
        # Create order lines
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
        
        # Mark plan as done
        plan_line.plan_id.action_done()
        
        # Return action to view the created PO
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'purchase.order',
            'res_id': po.id,
            'target': 'current',
        }