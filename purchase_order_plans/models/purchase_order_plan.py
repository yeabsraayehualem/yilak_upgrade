from odoo import models, fields, api, _

class PurchaseOrderPlan(models.Model):
    _name = 'purchase.order.plan'
    _description = 'Purchase Order Plan'

    name = fields.Char(string='Plan Name', required=True)
    planned_by = fields.Many2one('res.users', string='Planned By', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    planned_date = fields.Date(string='Planned Date', default=fields.Date.context_today)
    description = fields.Text()
    line_ids = fields.One2many('purchase.order.plan.line', 'plan_id', string='Rounds/Lines')
    state = fields.Selection([('draft', 'Draft'), ('scheduled', 'Scheduled'), ('done', 'Done')], default='draft')

    def action_schedule(self):
        self.state = 'scheduled'

    def action_done(self):
        self.state = 'done'