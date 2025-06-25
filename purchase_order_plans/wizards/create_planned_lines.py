from odoo import models, fields, api

class CreatePlannedLines(models.Model):
    _name = 'create.planned.lines'
    _description = 'Create Planned Lines Wizard'

    plan_id = fields.Many2one('purchase.order.plan', required=True, readonly=True,ondelete='cascade')
    plan_state = fields.Selection(
        related='plan_id.state',
        string='Plan Status',
        readonly=True,
    )
    po_count = fields.Integer(compute='_compute_po_count')
    round_name = fields.Char(required=True)
    vendor_id = fields.Many2one('res.partner', string='Vendor', domain=[('supplier_rank', '>', 0)], required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    exchange_rate = fields.Float(string='Exchange Rate', default=1.0)
    container_qty = fields.Integer(string='Number of Containers')
    scheduled_date = fields.Date()
    product_line_ids = fields.One2many('create.planned.lines.product', 'wizard_id', string='Products')
    proforma_no = fields.Char(stirng="Proforma No.")
    proforma_attachment = fields.Binary(string='Attachemnt')
    purchase_ordered = fields.Boolean(default=False)
    def action_create(self):
        _logger.info("=== STARTING ACTION_CREATE ===")
        # ... existing code ...
        _logger.info(f"Created plan line ID: {plan_line.id}")
        # ... after product lines creation ...
        _logger.info(f"Created {len(self.product_line_ids)} product lines")
        self.env.cr.flush()
        _logger.info("Flushed transaction")
        # First create the plan line
        plan_line = self.env['purchase.order.plan.line'].create({
            'plan_id': self.plan_id.id,
            'round_name': self.round_name,
            'vendor_id': self.vendor_id.id,
            'container_qty': self.container_qty,
            'scheduled_date': self.scheduled_date,
        })
    
    # Create product lines
        for p in self.product_line_ids:
            self.env['purchase.order.plan.line.product'].create({
                'plan_line_id': plan_line.id,
                'product_id': p.product_id.id,
                'product_qty': p.product_qty,
                'price_unit': p.price_unit,
            })
    
    # Schedule the plan
        self.plan_id.action_schedule()
    
    # FLUSH the transaction to ensure records are committed
        self.env.cr.flush()
    
    # Return the convert to PO wizard with the NEWLY CREATED plan_line_id
        return {
            'name': 'Convert to PO',
            'type': 'ir.actions.act_window',
            'res_model': 'convert.to.po',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_plan_line_id': plan_line.id
            },
        }


    

    def _compute_po_count(self):
        for record in self:
            # Adjust domain to match your specific POs if needed
            record.po_count = self.env['purchase.order'].search_count([])


    def view_ordered_products(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Orders',
            'res_model': 'purchase.order',
            'view_mode': 'tree,form',
            # 'domain': [('plan_id', '=', self.id)],  
            'context': {'search_default_group_by_partner': 1},
        }

    @api.constrains('exchange_rate')
    def _check_exchange_rate(self):
        for rec in self:
            if rec.exchange_rate <= 0:
                raise ValidationError("Exchange rate must be positive")
            if rec.exchange_rate > 1000: 
                raise ValidationError("Exchange rate is unrealistically high")

    @api.constrains('container_qty')
    def _check_container_qty(self):
        for rec in self:
            if rec.container_qty < 0:
                raise ValidationError("Container quantity cannot be negative")
            if rec.container_qty > 100: 
                raise ValidationError("Container quantity exceeds maximum allowed")
    def action_open_convert_wizard(self):
        if not self.proforma_no or not self.proforma_attachment:
            raise ValidationError("Proforma attachment and proforma number is required!!")

        po=  self.env['purchase.order'].create({
            'partner_id': self.vendor_id.id,
        
        })
        for line in self.product_line_ids:
            self.env['purchase.order.line'].create({
                'product_id': line.product_id.id,
                'product_qty': line.product_qty,
                'price_unit':line.price_unit,
                'order_id': po.id
            })
        self.purchase_ordered = True