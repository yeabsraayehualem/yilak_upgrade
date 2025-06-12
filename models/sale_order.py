from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    approval_requested = fields.Boolean(
        string="Approval Requested", default=False, readonly=True
    )

    def action_request_approval(self):
        """Request approval from Sales Approval Manager."""
        self.write({'approval_requested': True})
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            summary=_("Approval Requested"),
            note=_("Please approve the sales order %s.") % self.name,
            user_id=self.env.ref('base.user_admin').id,  # Temporary admin user
        )

    def action_approve(self):
        """Approve the sales order and set to Quotation Sent."""
        if not self.env.user.has_group('custom_sale_approval_void.group_sales_approval_manager'):
            raise UserError(_("Only Sales Approval Managers can approve sales orders."))
        self.write({'state': 'sent', 'approval_requested': False})
        self.activity_feedback(['mail.mail_activity_data_todo'])

    def action_confirm(self):
        """Override confirm to check approval."""
        for order in self:
            if order.state not in ('sent', 'sale'):
                raise UserError(
                    _("The sales order must be approved and sent before confirmation.")
                )
        return super(SaleOrder, self).action_confirm()