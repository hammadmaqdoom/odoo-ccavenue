{
    'name': 'CCAvenue Payment Gateway',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Payment Acquirers',
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
        
        Modules Integration:
        - account: Invoice payments
        - website_sale: eCommerce checkout
        - website: General website payments
        - mail: Email notifications
        - portal: Customer portal payments
    """,
    'author': 'Digitaro',
    'website': 'https://digitaro.co',
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
    'data': [
        'security/ir.model.access.csv',
        'data/payment_method_data.xml',
        'data/payment_acquirer_data.xml',
        'data/mail_template_data.xml',
        'views/payment_acquirer_views.xml',
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
    'application': False,
    'license': 'LGPL-3',
    'external_dependencies': {
        'python': ['pycryptodome', 'requests']
    },
}