/*
React Native Integration Example for CCAvenue

1. Install dependencies:
npm install react-native-ccavenue

2. Create payment service:
*/

import { NativeModules } from 'react-native';

class CCavenuePaymentService {
  static baseUrl = 'https://your-odoo-instance.com';

  static async initiatePayment({
    orderId,
    amount,
    currency,
    customerDetails,
  }) {
    try {
      // Create transaction in Odoo
      const response = await fetch(`${this.baseUrl}/payment/transaction`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          reference: orderId,
          amount: amount,
          currency: currency,
          partner_data: customerDetails,
          provider_code: 'ccavenue',
        }),
      });

      const data = await response.json();
      const txId = data.transaction_id;

      // Get payment data for mobile SDK
      const paymentResponse = await fetch(`${this.baseUrl}/payment/ccavenue/mobile/initiate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tx_id: txId }),
      });

      const paymentData = await paymentResponse.json();

      if (paymentData.success) {
        return new Promise((resolve, reject) => {
          NativeModules.CCAvenueModule.startPayment(
            paymentData.payment_data,
            async (response) => {
              await this._handlePaymentResponse(response);
              resolve({ success: true, result: response });
            }
          );
        });
      }

      throw new Error('Failed to get payment data');
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  static async _handlePaymentResponse(responseData) {
    await fetch(`${this.baseUrl}/payment/ccavenue/mobile/callback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ response_data: responseData }),
    });
  }
}

// Usage in your React Native component:
import React from 'react';
import { View, Button, Alert } from 'react-native';

const CheckoutScreen = ({ navigation }) => {
  const handlePayment = async () => {
    const result = await CCavenuePaymentService.initiatePayment({
      orderId: 'ORD-001',
      amount: 100.00,
      currency: 'AED',
      customerDetails: {
        name: 'John Doe',
        email: 'john@example.com',
        phone: '+971501234567',
      },
    });

    if (result.success) {
      navigation.navigate('PaymentSuccess');
    } else {
      Alert.alert('Payment Failed', result.error);
    }
  };

  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <Button title="Pay with CCAvenue" onPressed={handlePayment} />
    </View>
  );
};

export default CheckoutScreen;