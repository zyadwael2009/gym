"""Paymob Payment Gateway Service"""
import requests
import hmac
import hashlib
import json
from app.config.paymob_config import PaymobConfig

class PaymobService:
    """Handle Paymob payment operations"""
    
    @staticmethod
    def get_auth_token():
        """Get authentication token from Paymob"""
        try:
            print(f"[PAYMOB] Requesting auth token from {PaymobConfig.AUTH_URL}")
            print(f"[PAYMOB] Using API_KEY: {PaymobConfig.API_KEY[:30]}...")
            
            response = requests.post(
                PaymobConfig.AUTH_URL,
                json={"api_key": PaymobConfig.API_KEY},
                timeout=30
            )
            print(f"[PAYMOB] Auth response status: {response.status_code}")
            print(f"[PAYMOB] Auth response: {response.text[:200]}")
            
            response.raise_for_status()
            data = response.json()
            token = data.get('token')
            print(f"[PAYMOB] Auth token received: {token[:20] if token else 'None'}...")
            return token
        except requests.exceptions.RequestException as e:
            print(f"[PAYMOB] Auth error: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"[PAYMOB] Error status: {e.response.status_code}")
                print(f"[PAYMOB] Error response: {e.response.text}")
            return None
    
    @staticmethod
    def create_order(auth_token, amount_cents, merchant_order_id):
        """Create an order in Paymob"""
        try:
            print(f"[PAYMOB] Creating order: {merchant_order_id}, amount: {amount_cents}")
            response = requests.post(
                PaymobConfig.ORDER_URL,
                json={
                    "auth_token": auth_token,
                    "delivery_needed": "false",
                    "amount_cents": str(amount_cents),
                    "currency": PaymobConfig.CURRENCY,
                    "merchant_order_id": merchant_order_id,
                    "items": []
                },
                timeout=30
            )
            print(f"[PAYMOB] Order response status: {response.status_code}")
            response.raise_for_status()
            data = response.json()
            order_id = data.get('id')
            print(f"[PAYMOB] Order created successfully: {order_id}")
            return order_id
        except requests.exceptions.RequestException as e:
            print(f"[PAYMOB] Order creation error: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"[PAYMOB] Error response: {e.response.text}")
            return None
    
    @staticmethod
    def get_payment_key(auth_token, order_id, amount_cents, billing_data, integration_id=None):
        """Get payment key for iFrame"""
        if integration_id is None:
            integration_id = PaymobConfig.CARD_INTEGRATION_ID
        
        try:
            print(f"[PAYMOB] Getting payment key for order: {order_id}, integration: {integration_id}")
            response = requests.post(
                PaymobConfig.PAYMENT_KEY_URL,
                json={
                    "auth_token": auth_token,
                    "amount_cents": str(amount_cents),
                    "expiration": 3600,
                    "order_id": str(order_id),
                    "billing_data": billing_data,
                    "currency": PaymobConfig.CURRENCY,
                    "integration_id": integration_id
                },
                timeout=30
            )
            print(f"[PAYMOB] Payment key response status: {response.status_code}")
            response.raise_for_status()
            data = response.json()
            payment_key = data.get('token')
            print(f"[PAYMOB] Payment key received: {payment_key[:20] if payment_key else 'None'}...")
            return payment_key
        except requests.exceptions.RequestException as e:
            print(f"[PAYMOB] Payment key error: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"[PAYMOB] Error response: {e.response.text}")
            return None
    
    @staticmethod
    def initiate_payment(amount, customer_data, subscription_id, payment_method='card'):
        """
        Initiate a payment transaction
        
        Args:
            amount: Amount in EGP (will be converted to cents)
            customer_data: Dict with customer info (name, email, phone)
            subscription_id: Subscription ID for tracking
            payment_method: 'card' or 'wallet'
        
        Returns:
            Dict with payment_token and iframe_url or None
        """
        print(f"[PAYMOB] Initiating payment: amount={amount}, method={payment_method}")
        
        # Demo mode for testing UI without real API calls
        if PaymobConfig.DEMO_MODE:
            print(f"[PAYMOB] DEMO MODE - Returning mock payment data")
            import time
            mock_order_id = f"DEMO-{int(time.time())}"
            mock_token = f"demo_token_{int(time.time())}"
            # Use local server for demo payment page
            demo_url = f"http://192.168.1.6:5000/api/paymob/demo/payment?token={mock_token}&amount={amount}"
            if subscription_id:
                demo_url += f"&payment_id={subscription_id}"
            return {
                'payment_token': mock_token,
                'iframe_url': demo_url,
                'order_id': mock_order_id,
                'amount_cents': int(float(amount) * 100)
            }
        
        # Convert amount to cents (Paymob uses cents)
        amount_cents = int(float(amount) * 100)
        
        # Step 1: Get auth token
        print(f"[PAYMOB] Step 1: Getting auth token...")
        auth_token = PaymobService.get_auth_token()
        if not auth_token:
            print(f"[PAYMOB] ERROR: Failed to get auth token")
            return None
        
        # Step 2: Create order
        import time
        timestamp = int(time.time() * 1000)  # Add milliseconds timestamp
        merchant_order_id = f"GYM-{subscription_id or 'NEW'}-{timestamp}"
        print(f"[PAYMOB] Step 2: Creating order with ID: {merchant_order_id}")
        order_id = PaymobService.create_order(auth_token, amount_cents, merchant_order_id)
        if not order_id:
            print(f"[PAYMOB] ERROR: Failed to create order")
            return None
        print(f"[PAYMOB] Order created: {order_id}")
        
        # Step 3: Prepare billing data
        billing_data = {
            "apartment": "NA",
            "email": customer_data.get('email', 'customer@gym.com'),
            "floor": "NA",
            "first_name": customer_data.get('first_name', 'Customer'),
            "street": "NA",
            "building": "NA",
            "phone_number": customer_data.get('phone', '+201000000000'),
            "shipping_method": "NA",
            "postal_code": "NA",
            "city": "Cairo",
            "country": "Egypt",
            "last_name": customer_data.get('last_name', 'User'),
            "state": "Cairo"
        }
        
        # Step 4: Get integration ID based on payment method
        integration_id = (PaymobConfig.MOBILE_WALLET_INTEGRATION_ID 
                         if payment_method == 'wallet' 
                         else PaymobConfig.CARD_INTEGRATION_ID)
        
        # Step 5: Get payment key
        payment_token = PaymobService.get_payment_key(
            auth_token, 
            order_id, 
            amount_cents, 
            billing_data,
            integration_id
        )
        
        if not payment_token:
            return None
        
        # Step 6: Generate payment URL based on method
        if payment_method == 'wallet':
            print(f"[PAYMOB] Generating mobile wallet URL")
            payment_url = PaymobConfig.get_mobile_wallet_url(payment_token)
        else:
            print(f"[PAYMOB] Generating card iFrame URL")
            payment_url = PaymobConfig.get_iframe_url(payment_token)
        
        return {
            'payment_token': payment_token,
            'iframe_url': payment_url,  # This contains either iFrame or mobile wallet URL
            'order_id': order_id,
            'amount_cents': amount_cents,
            'payment_method': payment_method
        }
    
    @staticmethod
    def verify_callback(query_params):
        """
        Verify Paymob callback using HMAC
        
        Args:
            query_params: Dict of callback parameters
        
        Returns:
            Boolean indicating if callback is valid
        """
        try:
            # Extract HMAC from callback
            received_hmac = query_params.get('hmac', '')
            
            # Build string for HMAC calculation
            hmac_fields = [
                'amount_cents',
                'created_at',
                'currency',
                'error_occured',
                'has_parent_transaction',
                'id',
                'integration_id',
                'is_3d_secure',
                'is_auth',
                'is_capture',
                'is_refunded',
                'is_standalone_payment',
                'is_voided',
                'order',
                'owner',
                'pending',
                'source_data_pan',
                'source_data_sub_type',
                'source_data_type',
                'success'
            ]
            
            # Build concatenated string
            hmac_string = ""
            for field in hmac_fields:
                value = query_params.get(field, '')
                # Convert boolean to lowercase string
                if isinstance(value, bool):
                    value = str(value).lower()
                hmac_string += str(value)
            
            # Calculate HMAC
            calculated_hmac = hmac.new(
                PaymobConfig.HMAC_SECRET.encode('utf-8'),
                hmac_string.encode('utf-8'),
                hashlib.sha512
            ).hexdigest()
            
            # Compare
            return hmac.compare_digest(calculated_hmac, received_hmac)
            
        except Exception as e:
            print(f"[PAYMOB] HMAC verification error: {str(e)}")
            return False
    
    @staticmethod
    def parse_callback_data(data):
        """
        Parse Paymob callback data
        
        Returns:
            Dict with parsed transaction info
        """
        obj = data.get('obj', {})
        
        return {
            'success': obj.get('success', False),
            'transaction_id': obj.get('id'),
            'order_id': obj.get('order', {}).get('id') if isinstance(obj.get('order'), dict) else obj.get('order'),
            'amount_cents': obj.get('amount_cents'),
            'currency': obj.get('currency'),
            'is_refunded': obj.get('is_refunded', False),
            'is_voided': obj.get('is_voided', False),
            'error_occured': obj.get('error_occured', False),
            'pending': obj.get('pending', False),
            'payment_method': obj.get('source_data', {}).get('type', 'unknown')
        }
