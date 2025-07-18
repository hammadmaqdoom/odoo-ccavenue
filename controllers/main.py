import json
import logging
from odoo import http
from odoo.http import request
from odoo.addons.payment import utils as payment_utils

_logger = logging.getLogger(__name__)

class CCavenueController(http.Controller):

    @http.route('/payment/ccavenue/redirect/<int:tx_id>', type='http', auth='public')
    def ccavenue_redirect(self, tx_id, **kwargs):
        """Redirect to CCAvenue payment form"""
        tx = request.env['payment.transaction'].sudo().browse(tx_id)
        if not tx.exists():
            return request.redirect('/payment/status')
        
        rendering_values = tx._get_specific_rendering_values({})
        
        # Prepare form data
        form_data = {
            'merchant_id': rendering_values['merchant_id'],
            'order_id': rendering_values['order_id'],
            'amount': rendering_values['amount'],
            'currency': rendering_values['currency'],
            'redirect_url': rendering_values['redirect_url'],
            'cancel_url': rendering_values['cancel_url'],
            'billing_name': rendering_values['billing_name'],
            'billing_address': rendering_values['billing_address'],
            'billing_city': rendering_values['billing_city'],
            'billing_state': rendering_values['billing_state'],
            'billing_country': rendering_values['billing_country'],
            'billing_tel': rendering_values['billing_tel'],
            'billing_email': rendering_values['billing_email'],
        }
        
        # Convert to query string and encrypt
        form_string = '&'.join([f"{k}={v}" for k, v in form_data.items()])
        enc_request = tx.provider_id._ccavenue_encrypt(form_string)
        
        ccavenue_url = 'https://test.ccavenue.ae/transaction/transaction.do?command=initiateTransaction' if tx.provider_id.state == 'test' else 'https://secure.ccavenue.ae/transaction/transaction.do?command=initiateTransaction'
        
        return request.render('payment_ccavenue.ccavenue_redirect', {
            'enc_request': enc_request,
            'access_code': rendering_values['access_code'],
            'ccavenue_url': ccavenue_url
        })

    @http.route('/payment/ccavenue/return', type='http', auth='public', csrf=False, methods=['GET', 'POST'])
    def ccavenue_return(self, **kwargs):
        """Handle return from CCAvenue payment"""
        _logger.info("CCAvenue return data received")
        
        enc_resp = kwargs.get('encResp')
        if not enc_resp:
            return request.redirect('/payment/status')
        
        provider = request.env['payment.provider'].sudo().search([
            ('code', '=', 'ccavenue'),
            ('state', 'in', ['enabled', 'test'])
        ], limit=1)
        
        if not provider:
            return request.redirect('/payment/status')
        
        try:
            decrypted_data = provider._ccavenue_decrypt(enc_resp)
            response_data = dict(
                item.split('=', 1) for item in decrypted_data.split('&') if '=' in item
            )
            
            order_id = response_data.get('order_id')
            tx = request.env['payment.transaction'].sudo().search([
                ('reference', '=', order_id)
            ], limit=1)
            
            if tx:
                tx._process_notification_data({'encResp': enc_resp})
                return request.redirect(f'/payment/status/{tx.id}')
            
        except Exception as e:
            _logger.error("CCAvenue return processing failed: %s", str(e))
        
        return request.redirect('/payment/status')

    @http.route('/payment/ccavenue/cancel', type='http', auth='public', csrf=False)
    def ccavenue_cancel(self, **kwargs):
        """Handle cancel from CCAvenue payment"""
        _logger.info("CCAvenue cancel received")
        return request.redirect('/shop/payment')

    @http.route('/payment/ccavenue/mobile/initiate', type='json', auth='public')
    def ccavenue_mobile_initiate(self, **kwargs):
        """API endpoint for mobile app payment initiation"""
        try:
            tx_id = kwargs.get('tx_id')
            tx = request.env['payment.transaction'].sudo().browse(tx_id)
            
            if not tx.exists():
                return {'error': 'Transaction not found'}
                
            payment_values = tx._get_specific_rendering_values({})
            
            return {
                'success': True,
                'payment_data': payment_values
            }
            
        except Exception as e:
            _logger.error("Mobile payment initiation failed: %s", str(e))
            return {'error': str(e)}

    @http.route('/payment/ccavenue/mobile/callback', type='json', auth='public')
    def ccavenue_mobile_callback(self, **kwargs):
        """Handle mobile SDK payment callback"""
        try:
            response_data = kwargs.get('response_data')
            if isinstance(response_data, str):
                response_data = json.loads(response_data)
                
            order_id = response_data.get('order_id')
            tx = request.env['payment.transaction'].sudo().search([
                ('reference', '=', order_id)
            ], limit=1)
            
            if tx:
                tx._process_notification_data(response_data)
                return {'success': True, 'status': tx.state}
            else:
                return {'error': 'Transaction not found'}
                
        except Exception as e:
            _logger.error("Mobile callback processing failed: %s", str(e))
            return {'error': str(e)}
