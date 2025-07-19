import hashlib
import json
import logging
import subprocess
import sys
import base64
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('ccavenue', 'CCAvenue')],
        ondelete={'ccavenue': 'set default'}
    )
    ccavenue_merchant_id = fields.Char(
        string='Merchant ID',
        help='CCAvenue Merchant ID',
        required_if_provider='ccavenue',
        groups='base.group_system'
    )
    ccavenue_access_code = fields.Char(
        string='Access Code',
        help='CCAvenue Access Code',
        required_if_provider='ccavenue',
        groups='base.group_system'
    )
    ccavenue_working_key = fields.Char(
        string='Working Key',
        help='CCAvenue Working Key for encryption',
        required_if_provider='ccavenue',
        groups='base.group_system'
    )

    @api.model
    def create(self, vals):
        """Override create to check dependencies"""
        if vals.get('code') == 'ccavenue':
            self._check_dependencies()
        return super().create(vals)

    def write(self, vals):
        """Override write to check dependencies"""
        if vals.get('code') == 'ccavenue' or (self.code == 'ccavenue' and any(k.startswith('ccavenue_') for k in vals.keys())):
            self._check_dependencies()
        return super().write(vals)

    def _get_supported_currencies(self):
        """Override to return supported currencies for CCAvenue"""
        supported_currencies = super()._get_supported_currencies()
        if self.code == 'ccavenue':
            supported_currencies = supported_currencies.filtered(
                lambda c: c.name in ['AED', 'USD', 'EUR', 'GBP', 'INR']
            )
        return supported_currencies

    def _ccavenue_get_api_url(self):
        """Get API URL based on state"""
        if self.state == 'test':
            return "https://test.ccavenue.ae/transaction/appV1.do"
        return "https://secure.ccavenue.ae/transaction/appV1.do"

    def _ccavenue_encrypt(self, plain_text):
        key = self.ccavenue_working_key[:16].ljust(16, '0')
        iv = '0000000000000000'
        try:
            result = subprocess.run(
                ['openssl', 'enc', '-aes-128-cbc', '-K', key.encode().hex(), '-iv', iv.encode().hex(), '-nosalt', '-base64'],
                input=plain_text.encode(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            return result.stdout.decode().strip()
        except subprocess.CalledProcessError as e:
            raise UserError(f"Encryption failed: {e.stderr.decode()}")

    def _ccavenue_decrypt(self, encrypted_text):
        key = self.ccavenue_working_key[:16].ljust(16, '0')
        iv = '0000000000000000'
        try:
            result = subprocess.run(
                ['openssl', 'enc', '-aes-128-cbc', '-d', '-K', key.encode().hex(), '-iv', iv.encode().hex(), '-nosalt', '-base64'],
                input=encrypted_text.encode(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            return result.stdout.decode().strip()
        except subprocess.CalledProcessError as e:
            raise UserError(f"Decryption failed: {e.stderr.decode()}")


    def _ccavenue_generate_tracking_id(self, tx_values):
        """Generate tracking ID via CCAvenue API"""
        try:
            import requests
        except ImportError:
            raise UserError(_("Missing requests library. Please install: pip install requests"))
        
        url = f"{self._ccavenue_get_api_url()}?command=generateTrackingId"
        
        plain_data = {
            "merchant_id": self.ccavenue_merchant_id,
            "order_id": tx_values['reference'],
            "tid": "",
            "currency": tx_values.get('currency_name', 'AED'),
            "amount": float(tx_values['amount'])
        }
        
        enc_request = self._ccavenue_encrypt(json.dumps(plain_data))
        
        payload = {
            "access_code": self.ccavenue_access_code,
            "encRequest": enc_request
        }
        
        try:
            response = requests.post(url, data=payload, timeout=30)
            response.raise_for_status()
            
            response_data = response.json()
            if response_data.get('status') == 'success':
                enc_resp = response_data['data']['encResp']
                decrypted_resp = json.loads(self._ccavenue_decrypt(enc_resp))
                return decrypted_resp.get('tracking_id')
            else:
                raise ValidationError(_("Failed to generate tracking ID"))
                
        except Exception as e:
            _logger.error("CCAvenue tracking ID generation failed: %s", str(e))
            raise ValidationError(_("Payment gateway communication error"))