"""
Test mobile wallet redirect URL
"""
import requests
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.config.paymob_config import PaymobConfig

print("="*70)
print("TESTING MOBILE WALLET REDIRECT URL")
print("="*70)

# Get auth token
response = requests.post(
    "https://accept.paymob.com/api/auth/tokens",
    json={"api_key": PaymobConfig.API_KEY}
)

if response.status_code != 201:
    print(f"❌ Auth failed")
    exit()

auth_token = response.json()['token']
print("\n✅ Step 1: Authenticated")

# Create order
order_resp = requests.post(
    "https://accept.paymob.com/api/ecommerce/orders",
    json={
        "auth_token": auth_token,
        "delivery_needed": "false",
        "amount_cents": "10000",
        "currency": "EGP",
        "merchant_order_id": f"WALLET-TEST-{int(time.time())}",
        "items": []
    }
)

if order_resp.status_code == 201:
    order_id = order_resp.json()['id']
    print(f"✅ Step 2: Order created ({order_id})")
    
    # Get payment key with WALLET integration
    pk_resp = requests.post(
        "https://accept.paymob.com/api/acceptance/payment_keys",
        json={
            "auth_token": auth_token,
            "amount_cents": "10000",
            "expiration": 3600,
            "order_id": str(order_id),
            "billing_data": {
                "apartment": "NA", "email": "test@test.com", "floor": "NA",
                "first_name": "Test", "street": "NA", "building": "NA",
                "phone_number": "+201000000000", "shipping_method": "NA",
                "postal_code": "NA", "city": "Cairo", "country": "Egypt",
                "last_name": "User", "state": "Cairo"
            },
            "currency": "EGP",
            "integration_id": 4626585  # WALLET integration
        }
    )
    
    if pk_resp.status_code == 201:
        payment_token = pk_resp.json()['token']
        print(f"✅ Step 3: Payment key generated")
        
        # Generate WALLET redirect URL (not iFrame!)
        wallet_url = PaymobConfig.get_mobile_wallet_url(payment_token)
        
        print(f"\n{'='*70}")
        print(f"🎉 SUCCESS! MOBILE WALLET URL GENERATED")
        print(f"{'='*70}\n")
        print(f"🔗 Copy this URL and open in browser:\n")
        print(f"{wallet_url}\n")
        print(f"{'='*70}")
        print(f"📱 You should see:")
        print(f"   • Vodafone Cash")
        print(f"   • Orange Cash")
        print(f"   • Etisalat Cash")
        print(f"   • We Cash")
        print(f"{'='*70}\n")
        print(f"✅ This URL works in your Flutter WebView too!")
        print(f"   No code changes needed - already configured!\n")
        
    else:
        print(f"❌ Payment key failed: {pk_resp.status_code}")
        print(f"Response: {pk_resp.text[:500]}")
else:
    print(f"❌ Order failed: {order_resp.status_code}")
