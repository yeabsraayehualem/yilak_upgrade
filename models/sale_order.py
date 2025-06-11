from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        selection_add=[
            ('waiting_approval', 'Waiting for Approval'),
            ('approved', 'Approved'),
        ],
        ondelete={'waiting_approval': 'set default', 'approved': 'set default'}
    )
    approval_requested = fields.Boolean(
        string="Approval Requested", default=False, readonly=True
    )

    from odoo import models, fields, api, _
    from odoo.exceptions import UserError

    class SaleOrder(models.Model):
        _inherit = 'sale.order'

        state = fields.Selection(
            selection_add=[
                ('waiting_approval', 'Waiting for Approval'),
                ('approved', 'Approved'),
            ],
            ondelete={'waiting_approval': 'set default', 'approved': 'set default'}
        )
        approval_requested = fields.Boolean(
            string="Approval Requested", default=False, readonly=True
        )

        def action_request_approval(self):
            """Request approval from Sales Manager."""
            for order in self:
                if not order.order_line:
                    raise UserError(_("You cannot request approval for a sales order without any products."))

                # Check if all lines have products
                for line in order.order_line:
                    if not line.product_id:
                        raise UserError(_("All order lines must have a product before requesting approval."))

            self.write({'approval_requested': True, 'state': 'waiting_approval'})
            # Assign activity to a user in the Sales Approval Manager group
            approval_group = self.env.ref('custom_sale_approval_void.group_sales_approval_manager')
            approval_user = approval_group.users[:1] or self.env.ref('base.user_admin')
            self.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=_("Approval Requested"),
                note=_("Please approve the sales order %s.") % self.name,
                user_id=approval_user.id,
            )

        def action_approve(self):
            """Approve the sales order."""
            if not self.env.user.has_group('custom_sale_approval_void.group_sales_approval_manager'):
                raise UserError(_("Only Sales Approval Managers can approve sales orders."))
            self.write({'state': 'approved', 'approval_requested': False})
            self.activity_feedback(['mail.mail_activity_data_todo'])

        def action_confirm(self):
            """Override confirm to check approval."""
            for order in self:
                if order.state not in ('approved', 'sale'):
                    raise UserError(
                        _("The sales order must be approved before confirmation.")
                    )
            return super(SaleOrder, self).action_confirm()
    def action_approve(self):
        """Approve the sales order."""
        if not self.env.user.has_group('custom_sale_approval_void.group_sales_approval_manager'):
            raise UserError(_("Only Sales Approval Managers can approve sales orders."))
        self.write({'state': 'approved', 'approval_requested': False})
        self.activity_feedback(['mail.mail_activity_data_todo'])

    def action_confirm(self):
        """Override confirm to check approval."""
        for order in self:
            if order.state not in ('approved', 'sale'):
                raise UserError(
                    _("The sales order must be approved before confirmation.")
                )
        return super(SaleOrder, self).action_confirm()
