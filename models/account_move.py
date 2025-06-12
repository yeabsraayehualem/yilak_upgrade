from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_void_invoice(self):
        """Void the invoice."""
        if self.state != 'posted':
            raise UserError(_("Only posted invoices can be voided."))
        if self.payment_state in ('paid', 'in_payment'):
            raise UserError(_("Cannot void a paid or partially paid invoice."))
        # Create a reversal move
        reversal = self.with_context(active_test=False)._reverse_moves(
            default_values_list=[{
                'ref': _('Void of %s') % self.name,
                'date': fields.Date.context_today(self),
            }],
            cancel=True
        )
        self.write({'state': 'cancel'})
        return reversal