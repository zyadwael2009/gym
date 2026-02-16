"""Check what type integration 4626585 actually is"""
import requests
import sys
import os

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.config.paymob_config import PaymobConfig

API_KEY = PaymobConfig.API_KEY

print("="*70)
print("CHECKING INTEGRATION 4626585")
print("="*70)

# Get auth token
response = requests.post(
    "https://accept.paymob.com/api/auth/tokens",
    json={"api_key": API_KEY}
)

if response.status_code != 201:
    print(f"❌ Auth failed: {response.status_code}")
    print(response.text)
    exit()

auth_token = response.json()['token']
print("\n✅ Authenticated")
print("\nNow let's see what happens when we use integration 4626585...")
print("\nCreating test order and payment key with integration 4626585:")
print("-"*70)

# Create order
import time
order_resp = requests.post(
    "https://accept.paymob.com/api/ecommerce/orders",
    json={
        "auth_token": auth_token,
        "delivery_needed": "false",
        "amount_cents": "10000",
        "currency": "EGP",
        "merchant_order_id": f"TEST-{int(time.time())}",
        "items": []
    }
)

if order_resp.status_code == 201:
    order_id = order_resp.json()['id']
    print(f"✅ Order created: {order_id}")
    
    # Get payment key with wallet integration
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
            "integration_id": 4626585  # Your "wallet" integration
        }
    )
    
    if pk_resp.status_code == 201:
        payment_token = pk_resp.json()['token']
        iframe_url = f"https://accept.paymob.com/api/acceptance/iframes/859704?payment_token={payment_token}"
        
        print(f"✅ Payment key generated successfully")
        print(f"\n🔗 Payment URL:")
        print(f"   {iframe_url}")
        print(f"\n📋 INSTRUCTIONS:")
        print(f"   1. Copy the URL above")
        print(f"   2. Open it in your browser")
        print(f"   3. Check what payment options appear:")
        print(f"      - If you see CARD FORM → Integration 4626585 is configured as CARD")
        print(f"      - If you see WALLET OPTIONS (Vodafone, Orange, etc) → It's correct")
        print(f"\n⚠️  If it shows cards, integration 4626585 is NOT a mobile wallet integration!")
        print(f"   You need to create a NEW mobile wallet integration in Paymob dashboard.")
    else:
        print(f"❌ Failed to get payment key: {pk_resp.status_code}")
        print(pk_resp.text)
else:
    print(f"❌ Failed to create order: {order_resp.status_code}")

print("\n" + "="*70)
print("NEXT STEPS:")
print("="*70)
print("1. Open the URL above in a browser")
print("2. See what payment method appears")
print("3. If it shows cards instead of wallets:")
print("   → Integration 4626585 is the wrong type")
print("   → Create a NEW 'Mobile Wallets' integration")
print("   → Update MOBILE_WALLET_INTEGRATION_ID with the new ID")
print("="*70)
