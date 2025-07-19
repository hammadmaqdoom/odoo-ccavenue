# CCAvenue Payment Gateway for Odoo 18

## Installation Instructions

### Prerequisites
1. Odoo 18.0 or later
2. Python 3.8+
3. Required Python packages:
   ```bash
   pip install pycryptodome requests
   ```

### Installation Steps

1. **Download and Extract**
   - Extract the module to your Odoo addons directory
   - Ensure the folder is named `payment_ccavenue`

2. **Update Addons List**
   ```bash
   # Restart Odoo service
   sudo service odoo restart
   
   # Or update apps list from Odoo interface
   # Settings > Apps > Update Apps List
   ```

3. **Install Module**
   - Go to Apps menu
   - Search for "CCAvenue Payment Gateway"
   - Click Install

4. **Configure Payment Provider**
   - Go to Accounting > Configuration > Payment Providers
   - Find "CCAvenue" provider
   - Configure the following fields:
     - **State**: Set to Test (for testing) or Enabled (for production)
     - **Merchant ID**: Your CCAvenue merchant ID
     - **Access Code**: Your CCAvenue access code
     - **Working Key**: Your CCAvenue working key
   - Save the configuration

### Testing

1. **Test Web Payments**
   - Create a sale order
   - Go to eCommerce and add items to cart
   - Proceed to checkout and select CCAvenue
   - Complete the payment flow

2. **Test Invoice Payments**
   - Create and post an invoice
   - Click "Pay with CCAvenue" button
   - Complete the payment

3. **Test Mobile Integration**
   - Use the provided Flutter/React Native examples
   - Test the mobile payment flow

### Configuration Options

#### Email Notifications
The module automatically sends email notifications on successful payments. The template can be customized at:
- Technical > Email > Email Templates > "CCAvenue Payment Success"

#### Supported Currencies
- AED (UAE Dirham) - Primary
- USD (US Dollar)
- EUR (Euro)
- GBP (British Pound)
- INR (Indian Rupee)

#### Security Features
- AES-128 encryption for all communications
- SHA-512 hashing for request validation
- Secure webhook handling
- IP whitelisting support

### Troubleshooting

#### Common Issues

1. **"Module not found" error**
   - Ensure the module is in the correct addons path
   - Restart Odoo service
   - Update apps list

2. **"Encryption failed" error**
   - Verify the working key is correct
   - Check that pycryptodome is installed

3. **"Payment gateway communication error"**
   - Verify internet connectivity
   - Check CCAvenue credentials
   - Ensure URLs are accessible

4. **Mobile SDK issues**
   - Verify native SDK installation
   - Check API endpoint URLs
   - Ensure proper CORS settings

#### Logs and Debugging
- Enable developer mode for detailed error messages
- Check Odoo logs: `/var/log/odoo/odoo.log`
- Enable payment debugging in Odoo settings

### Support
For support and customization:
- Email: hammadmaqdoom@digitaro.co
- Documentation: Check CCAvenue official documentation
- Odoo Community: https://www.odoo.com/forum

## File Structure
```
payment_ccavenue/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── main.py
├── data/
│   ├── mail_template_data.xml
│   ├── payment_provider_data.xml
│   └── payment_method_data.xml
├── models/
│   ├── __init__.py
│   ├── account_move.py
│   ├── payment_provider.py
│   ├── payment_transaction.py
│   └── sale_order.py
├── security/
│   └── ir.model.access.csv
├── static/
│   ├── description/
│   │   ├── icon.png
│   │   └── index.html
│   └── src/
│       ├── css/
│       │   ├── backend.css
│       │   └── payment_form.css
│       ├── img/
│       │   └── ccavenue_logo.png
│       └── js/
│           └── payment_form.js
├── views/
│   ├── account_move_views.xml
│   ├── payment_provider_views.xml
│   ├── payment_ccavenue_templates.xml
│   ├── payment_transaction_views.xml
│   ├── portal_templates.xml
│   ├── sale_order_views.xml
│   └── website_payment_templates.xml
├── mobile_examples/
│   ├── flutter_integration.dart
│   └── react_native_integration.js
└── INSTALLATION.md
```