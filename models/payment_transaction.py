import json
import logging
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    ccavenue_tracking_id = fields.Char('CCAvenue Tracking ID', readonly=True)

    def _get_specific_rendering_values(self, processing_values):
        """Override to provide CCAvenue specific values"""
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'ccavenue':
            return res

        # Generate tracking ID
        tx_values = {
            'reference': self.reference,
            'amount': self.amount,
            'currency_name': self.currency_id.name
        }
        tracking_id = self.provider_id._ccavenue_generate_tracking_id(tx_values)
        self.ccavenue_tracking_id = tracking_id

        # Generate request hash
        request_hash = self.provider_id._ccavenue_generate_request_hash(
            tracking_id, self.currency_id.name, self.amount
        )

        base_url = self.provider_id.get_base_url()
        ccavenue_values = {
            'merchant_id': self.provider_id.ccavenue_merchant_id,
            'access_code': self.provider_id.ccavenue_access_code,
            'tracking_id': tracking_id,
            'request_hash': request_hash,
            'order_id': self.reference,
            'amount': str(self.amount),
            'currency': self.currency_id.name,
            'customer_id': self.partner_id.email or str(self.partner_id.id),
            'billing_name': self.partner_id.name or '',
            'billing_address': self._get_formatted_address(self.partner_id),
            'billing_city': self.partner_id.city or '',
            'billing_state': self.partner_id.state_id.name or '',
            'billing_country': self.partner_id.country_id.name or '',
            'billing_tel': self.partner_id.phone or self.partner_id.mobile or '',
            'billing_email': self.partner_id.email or '',
            'redirect_url': f"{base_url}/payment/ccavenue/return",
            'cancel_url': f"{base_url}/payment/ccavenue/cancel",
        }

        res.update(ccavenue_values)
        return res

    def _get_formatted_address(self, partner):
        """Get formatted address string"""
        address_parts = []
        if partner.street:
            address_parts.append(partner.street)
        if partner.street2:
            address_parts.append(partner.street2)
        return ', '.join(address_parts)

    def _process_notification_data(self, notification_data):
        """Process payment feedback from CCAvenue"""
        super()._process_notification_data(notification_data)
        if self.provider_code != 'ccavenue':
            return

        enc_response = notification_data.get('encResp')
        if enc_response:
            try:
                decrypted_data = self.provider_id._ccavenue_decrypt(enc_response)
                response_data = dict(
                    item.split('=', 1) for item in decrypted_data.split('&') if '=' in item
                )
                
                order_status = response_data.get('order_status')
                if order_status == 'Success':
                    self._set_done()
                elif order_status in ['Failure', 'Aborted']:
                    self._set_error(_("Payment failed: %s") % response_data.get('failure_message', ''))
                else:
                    self._set_pending()
                    
            except Exception as e:
                _logger.error("CCAvenue response processing failed: %s", str(e))
                self._set_error(_("Payment processing error"))
