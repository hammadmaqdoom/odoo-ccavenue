from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_pay_with_ccavenue(self):
        """Action to pay sale order with CCAvenue"""
        self.ensure_one()
        
        if self.state == 'cancel':
            raise UserError(_("Cannot pay a cancelled order"))

        provider = self.env['payment.provider'].search([
            ('code', '=', 'ccavenue'),
            ('state', 'in', ['enabled', 'test'])
        ], limit=1)
        
        if not provider:
            raise UserError(_("CCAvenue payment gateway is not configured"))

        return {
            'type': 'ir.actions.act_url',
            'url': f'/shop/payment?sale_order_id={self.id}',
            'target': 'self',
        }