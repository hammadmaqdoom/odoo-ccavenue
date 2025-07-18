import hashlib
import json
import logging
import subprocess
import sys
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

# Try importing dependencies with auto-install fallback
try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
    import base64
    import requests
except ImportError as e:
    missing_package = str(e).split("'")[1] if "'" in str(e) else "unknown"
    
    def install_missing_package():
        """Try to install missing package"""
        package_map = {
            'Crypto': 'pycryptodome',
            'requests': 'requests'
        }
        
        package_to_install = package_map.get(missing_package, missing_package)
        
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', package_to_install, '--user'
            ])
            # Re-import after installation
            if missing_package == 'Crypto':
                from Crypto.Cipher import AES
                from Crypto.Util.Padding import pad, unpad
                import base64
            elif missing_package == 'requests':
                import requests
            return True
        except Exception:
            return False
    
    # Try to auto-install
    if not install_missing_package():
        raise ImportError(f"Missing required package. Please install: pip install {package_map.get(missing_package, missing_package)}")

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
    def _check_dependencies(self):
        """Check if all dependencies are installed"""
        missing_deps = []
        
        try:
            from Crypto.Cipher import AES
            from Crypto.Util.Padding import pad, unpad
        except ImportError:
            missing_deps.append('pycryptodome')
        
        try:
            import requests
        except ImportError:
            missing_deps.append('requests')
        
        if missing_deps:
            raise UserError(_(
                "Missing required Python packages for CCAvenue integration. "
                "Please install: pip install %s"
            ) % ' '.join(missing_deps))
        
        return True

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
        """Encrypt data using AES-128 encryption"""
        try:
            from Crypto.Cipher import AES
            from Crypto.Util.Padding import pad
            import base64
        except ImportError:
            raise UserError(_("Missing encryption library. Please install: pip install pycryptodome"))
        
        working_key = self.ccavenue_working_key.encode()
        key = working_key[:16].ljust(16, b'0')
        
        cipher = AES.new(key, AES.MODE_CBC, b'0000000000000000')
        padded_text = pad(plain_text.encode(), AES.block_size)
        encrypted = cipher.encrypt(padded_text)
        return base64.b64encode(encrypted).decode()

    def _ccavenue_decrypt(self, encrypted_text):
        """Decrypt data using AES-128 decryption"""
        try:
            from Crypto.Cipher import AES
            from Crypto.Util.Padding import unpad
            import base64
        except ImportError:
            raise UserError(_("Missing encryption library. Please install: pip install pycryptodome"))
        
        working_key = self.ccavenue_working_key.encode()
        key = working_key[:16].ljust(16, b'0')
        
        cipher = AES.new(key, AES.MODE_CBC, b'0000000000000000')
        encrypted_data = base64.b64decode(encrypted_text)
        decrypted = cipher.decrypt(encrypted_data)
        return unpad(decrypted, AES.block_size).decode()

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

    def _ccavenue_generate_request_hash(self, tracking_id, currency, amount):
        """Generate request hash for mobile SDK"""
        data_string = f"{tracking_id}{currency}{amount}{self.ccavenue_working_key}"
        return hashlib.sha512(data_string.encode()).hexdigest()
