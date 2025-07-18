odoo.define('payment_ccavenue.payment_form', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var _t = core._t;

    publicWidget.registry.CCavenuePaymentForm = publicWidget.Widget.extend({
        selector: '.o_payment_form',
        events: {
            'change input[name="o_payment_radio"]': '_onPaymentMethodChange',
        },

        _onPaymentMethodChange: function (ev) {
            var $checkedRadio = this.$('input[name="o_payment_radio"]:checked');
            var providerCode = $checkedRadio.data('provider-code');
            
            // Hide all payment form details
            this.$('.o_payment_form_ccavenue').addClass('d-none');
            
            // Show the selected payment method details
            if (providerCode === 'ccavenue') {
                this.$('.o_payment_form_ccavenue').removeClass('d-none');
            }
        },
    });

    return publicWidget.registry.CCavenuePaymentForm;
});