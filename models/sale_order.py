from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    approval_requested = fields.Boolean(
        string="Approval Requested", default=False, readonly=True,
        help="Indicates if approval has been requested for this order"
    )
    approved_by = fields.Many2one('res.users', string="Approved By", readonly=True)
    approved_on = fields.Datetime(string="Approved On", readonly=True)

    def action_request_approval(self):
        for order in self:
            if order.state != 'draft':
                raise UserError(_("Approval can only be requested for draft orders."))
            if order.approval_requested:
                raise UserError(_("Approval has already been requested for this order."))

            order.write({'approval_requested': True})
            order.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=_("Approval Requested"),
                note=_("Please approve the sales order %s.") % order.name,
                user_id=self.env.ref('base.user_admin').id,
            )
            _logger.info("Approval requested for order %s", order.name)

    def action_approve(self):
        for order in self:
            if not self.env.user.has_group('custom_sale_approval_void.group_sales_approval_manager'):
                raise UserError(_("Only Sales Approval Managers can approve sales orders."))
            if not order.approval_requested:
                raise UserError(_("This order hasn't had approval requested."))
            if order.state != 'draft':
                raise UserError(_("Only draft orders can be approved."))

            order.write({
                'state': 'sent',
                'approval_requested': False,
                'approved_by': self.env.user.id,
                'approved_on': fields.Datetime.now()
            })
            order.activity_feedback(['mail.mail_activity_data_todo'])
            order.message_post(body=_("Sales order approved by %s.") % self.env.user.name)
            _logger.info("Order %s approved by %s", order.name, self.env.user.name)

    def action_confirm(self):
        for order in self:
            if order.state not in ('sent', 'sale'):
                raise UserError(_("The sales order must be approved (in 'sent' state) before confirmation."))
        return super().action_confirm()

    # def action_void_delivery(self):
    #     self.ensure_one()
    #     if not self.env.user.has_group('custom_sale_approval_void.group_sales_approval_manager'):
    #         raise UserError(_("Only Sales Approval Managers can void deliveries."))
    #     if self.state != 'sale':
    #         raise UserError(_("You can only void deliveries for confirmed sales orders."))
    #
    #     pickings = self.picking_ids.filtered(lambda p: p.state not in ['done', 'cancel'])
    #     if not pickings:
    #         raise UserError(_("No deliveries to void for this order."))
    #
    #     for picking in pickings:
    #         picking.action_cancel()
    #         _logger.info("Delivery %s voided for order %s", picking.name, self.name)
    #         self.message_post(body=_("Delivery %s has been voided.") % picking.name)
    #
    #     return {
    #         'type': 'ir.actions.client',
    #         'tag': 'display_notification',
    #         'params': {
    #             'title': _('Delivery Voided'),
    #             'message': _('The delivery has been successfully voided.'),
    #             'type': 'danger',
    #             'sticky': False,
    #         }
    #     }
    #
    # def action_void_invoice(self):
    #     self.ensure_one()
    #     if not self.env.user.has_group('custom_sale_approval_void.group_sales_approval_manager'):
    #         raise UserError(_("Permission error"))
    #
    #     if not self.invoice_ids:
    #         raise UserError(_("No invoices exist to void"))
    #
    #     invoices = self.invoice_ids.filtered(lambda inv: inv.state not in ['cancel', 'paid'])
    #     if not invoices:
    #         raise UserError(_("No invoices to void for this order."))
    #
    #     for invoice in invoices:
    #         invoice.button_cancel()
    #         _logger.info("Invoice %s voided for order %s", invoice.name, self.name)
    #         self.message_post(body=_("Invoice %s has been voided.") % invoice.name)
    #
    #     return {
    #         'type': 'ir.actions.client',
    #         'tag': 'display_notification',
    #         'params': {
    #             'title': _('Invoice Voided'),
    #             'message': _('The invoice has been successfully voided.'),
    #             'type': 'danger',
    #             'sticky': False,
    #         }
    #     }

    def action_void_all(self):
        self.ensure_one()
        if not self.env.user.has_group('custom_sale_approval_void.group_sales_approval_manager'):
            raise UserError(_("Only Sales Approval Managers can void sales orders."))

        if self.state != 'sale':
            raise UserError(_("You can only void sales orders that are in confirmed state."))

        # Void Deliveries
        pickings = self.picking_ids.filtered(lambda p: p.state not in ['done', 'cancel'])
        for picking in pickings:
            picking.action_cancel()
            _logger.info("Delivery %s voided for order %s", picking.name, self.name)
            self.message_post(body=_("Delivery %s has been voided.") % picking.name)

        # Void Invoices
        invoices = self.invoice_ids.filtered(lambda inv: inv.state not in ['cancel', 'paid'])
        for invoice in invoices:
            invoice.button_cancel()
            _logger.info("Invoice %s voided for order %s", invoice.name, self.name)
            self.message_post(body=_("Invoice %s has been voided.") % invoice.name)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Void Processed'),
                'message': _('Deliveries and invoices have been successfully voided.'),
                'type': 'danger',
                'sticky': False,
            }
        }
