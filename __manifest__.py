{
    'name': 'CCAvenue_Payment_Gateway',
    'version': '18.0.0.0.0',
    'category': 'Accounting/Payment Providers',
    'summary': 'CCAvenue Payment Gateway Integration for UAE',
    'description': """
        Complete CCAvenue Payment Gateway Integration
        ==========================================
        
        Features:
        - Invoice payments from portal
        - eCommerce checkout integration
        - Mobile SDK support (Flutter/React Native)
        - Website payment forms
        - Email notifications via mail module
        - Full encryption/decryption support
        - Test and production modes
        - Auto-install Python dependencies
        
        Dependencies:
        - pycryptodome: For AES encryption/decryption
        - requests: For API communications
        
        Modules Integration:
        - account: Invoice payments
        - website_sale: eCommerce checkout
        - website: General website payments
        - mail: Email notifications
        - portal: Customer portal payments
    """,
    'author': 'Digitaro',
    'website': 'https://www.digitaro.co/',
    'depends': [
        'base',
        'payment',
        'account',
        'website_sale',
        'website',
        'mail',
        'portal',
        'sale'
    ],
    'external_dependencies': {
        'python': ['requests']
    },
    'data': [
        'security/ir.model.access.csv',
        'data/payment_method_data.xml',
        'data/payment_provider_data.xml',
        'data/mail_template_data.xml',
        'views/payment_provider_views.xml',
        'views/payment_transaction_views.xml',
        'views/account_move_views.xml',
        'views/sale_order_views.xml',
        'views/payment_ccavenue_templates.xml',
        'views/website_payment_templates.xml',
        'views/portal_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'payment_ccavenue/static/src/css/payment_form.css',
            'payment_ccavenue/static/src/js/payment_form.js',
        ],
        'web.assets_backend': [
            'payment_ccavenue/static/src/css/backend.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
    # 'pre_init_hook': 'pre_init_hook',
    # 'post_init_hook': 'post_init_hook',
}