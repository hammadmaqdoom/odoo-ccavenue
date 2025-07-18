/*
Flutter Integration Example for CCAvenue

Add this to your Flutter project:

1. Add dependencies in pubspec.yaml:
dependencies:
  http: ^0.13.5
  crypto: ^3.0.2

2. Create CCAvenue payment service:
*/

import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/services.dart';

class CCavenuePaymentService {
  static const MethodChannel _channel = MethodChannel('plugin_ccavenue');
  static const String baseUrl = 'https://your-odoo-instance.com';

  static Future<Map<String, dynamic>> initiatePayment({
    required String orderId,
    required double amount,
    required String currency,
    required Map<String, String> customerDetails,
  }) async {
    try {
      // Create transaction in Odoo
      final response = await http.post(
        Uri.parse('$baseUrl/payment/transaction'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'reference': orderId,
          'amount': amount,
          'currency': currency,
          'partner_data': customerDetails,
          'provider_code': 'ccavenue',
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final txId = data['transaction_id'];

        // Get payment data for mobile SDK
        final paymentResponse = await http.post(
          Uri.parse('$baseUrl/payment/ccavenue/mobile/initiate'),
          headers: {'Content-Type': 'application/json'},
          body: json.encode({'tx_id': txId}),
        );

        if (paymentResponse.statusCode == 200) {
          final paymentData = json.decode(paymentResponse.body);
          
          if (paymentData['success']) {
            // Launch CCAvenue SDK
            final result = await _channel.invokeMethod('payCCAvenue', paymentData['payment_data']);
            
            // Send result back to Odoo
            await _handlePaymentResponse(result);
            
            return {'success': true, 'result': result};
          }
        }
      }
      
      throw Exception('Failed to initiate payment');
    } catch (e) {
      return {'success': false, 'error': e.toString()};
    }
  }

  static Future<void> _handlePaymentResponse(String responseData) async {
    await http.post(
      Uri.parse('$baseUrl/payment/ccavenue/mobile/callback'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'response_data': responseData}),
    );
  }
}

// Usage in your Flutter app:
class CheckoutPage extends StatefulWidget {
  @override
  _CheckoutPageState createState() => _CheckoutPageState();
}

class _CheckoutPageState extends State<CheckoutPage> {
  Future<void> _processPayment() async {
    final result = await CCavenuePaymentService.initiatePayment(
      orderId: 'ORD-001',
      amount: 100.00,
      currency: 'AED',
      customerDetails: {
        'name': 'John Doe',
        'email': 'john@example.com',
        'phone': '+971501234567',
      },
    );

    if (result['success']) {
      // Handle success
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => PaymentSuccessPage()),
      );
    } else {
      // Handle error
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Payment failed: ${result['error']}')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Checkout')),
      body: Center(
        child: ElevatedButton(
          onPressed: _processPayment,
          child: Text('Pay with CCAvenue'),
        ),
      ),
    );
  }
}
