from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_pay_with_ccavenue(self):
        """Action to pay invoice with CCAvenue"""
        self.ensure_one()
        if self.state != 'posted':
            raise UserError(_("You can only pay posted invoices"))
        
        if self.payment_state == 'paid':
            raise UserError(_("This invoice is already paid"))

        provider = self.env['payment.provider'].search([
            ('code', '=', 'ccavenue'),
            ('state', 'in', ['enabled', 'test'])
        ], limit=1)
        
        if not provider:
            raise UserError(_("CCAvenue payment gateway is not configured"))

        return {
            'type': 'ir.actions.act_url',
            'url': f'/my/invoices/{self.id}/pay',
            'target': 'self',
        }