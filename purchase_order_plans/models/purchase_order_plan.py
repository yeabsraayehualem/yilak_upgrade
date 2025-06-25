from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class PurchaseOrderPlan(models.Model):
    _name = 'purchase.order.plan'
    _description = 'Purchase Order Plan'

    name = fields.Char(string='Plan Name', required=True)
    planned_by = fields.Many2one('res.users', string='Planned By', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    planned_date = fields.Date(string='Planned Date', default=fields.Date.context_today)
    description = fields.Text()
    line_ids = fields.One2many('create.planned.lines', 'plan_id', string="Planned Lines")
    state = fields.Selection([('draft', 'Draft'), ('scheduled', 'Scheduled'), ('done', 'Done')], default='draft')
    count_plans= fields.Integer(default=1)

    def order_plans(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Planned Lines',
            'res_model': 'create.planned.lines',
            'view_mode': 'tree,form',
            'target': 'current',  
            'context': {
                'default_plan_id': self.id,
            },
        }
    
    def open_convert_po_wizard(self):
        self.ensure_one()
        if not self.line_ids:
             raise ValidationError(_("No planned lines available to convert"))
        # Optionally choose the first line or filter appropriately
        return {
            'name': 'Convert to PO',
            'type': 'ir.actions.act_window',
            'res_model': 'convert.to.po',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_plan_line_id': self.line_ids[0].id
            },
        }

    def action_schedule(self):
        self.state = 'scheduled'

    def action_done(self):
        self.state = 'done'
    
    def write(self, vals):
        if 'state' in vals:
            for rec in self:
                if vals['state'] == 'draft' and rec.state in ('scheduled', 'done'):
                    raise ValidationError(_("Cannot revert to draft once scheduled or done"))
                if vals['state'] == 'scheduled' and rec.state == 'done':
                    raise ValidationError(_("Cannot set to scheduled once done"))
        return super().write(vals)
