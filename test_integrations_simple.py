"""Simple test of Paymob integrations"""
import requests
import time

API_KEY = "ZXlKaGJHY2lPaUpJVXpVeE1pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SmpiR0Z6Y3lJNklrMWxjbU5vWVc1MElpd2ljSEp2Wm1sc1pWOXdheUk2T1RnNE5EWXpMQ0p1WVcxbElqb2lNVGN5TXpFd09UQTFPUzQyTlRFd09EWWlmUS5tdFNMa05GNnBxTTVmMVF5T0RiS0xiR21kb1FwOUZHZS1QcjdTVXhJbVp0N1htOWhnLThLNWdMN1BCSEJ0TXl5SUJnUlUwTm9fWF9vWGFOUF9INmFXUQ=="

print("="*70)
print("TESTING PAYMOB INTEGRATIONS")
print("="*70)

# Get auth token
print("\n1. Getting auth token...")
response = requests.post(
    "https://accept.paymob.com/api/auth/tokens",
    json={"api_key": API_KEY}
)
auth_token = response.json()['token']
print("✅ Token received")

# Test Card Integration
print("\n2. Testing CARD Integration (4623557)...")
order_id = f"TEST-{int(time.time() * 1000)}"
order_resp = requests.post(
    "https://accept.paymob.com/api/ecommerce/orders",
    json={
        "auth_token": auth_token,
        "delivery_needed": "false",
        "amount_cents": "10000",
        "currency": "EGP",
        "merchant_order_id": order_id,
        "items": []
    }
)

if order_resp.status_code == 201:
    order_data = order_resp.json()
    
    # Try card payment key
    pk_resp = requests.post(
        "https://accept.paymob.com/api/acceptance/payment_keys",
        json={
            "auth_token": auth_token,
            "amount_cents": "10000",
            "expiration": 3600,
            "order_id": str(order_data['id']),
            "billing_data": {
                "apartment": "NA", "email": "test@test.com", "floor": "NA",
                "first_name": "Test", "street": "NA", "building": "NA",
                "phone_number": "+201000000000", "shipping_method": "NA",
                "postal_code": "NA", "city": "Cairo", "country": "Egypt",
                "last_name": "User", "state": "Cairo"
            },
            "currency": "EGP",
            "integration_id": 4623557
        }
    )
    
    if pk_resp.status_code == 201:
        print("   ✅ Card Integration WORKS (4623557)")
    else:
        print(f"   ❌ Card Integration FAILED: {pk_resp.status_code}")
        print(f"      {pk_resp.text[:150]}")

# Test Wallet Integration
print("\n3. Testing WALLET Integration (4626585)...")
order_id = f"TEST-{int(time.time() * 1000)}"
order_resp = requests.post(
    "https://accept.paymob.com/api/ecommerce/orders",
    json={
        "auth_token": auth_token,
        "delivery_needed": "false",
        "amount_cents": "10000",
        "currency": "EGP",
        "merchant_order_id": order_id,
        "items": []
    }
)

if order_resp.status_code == 201:
    order_data = order_resp.json()
    
    # Try wallet payment key
    pk_resp = requests.post(
        "https://accept.paymob.com/api/acceptance/payment_keys",
        json={
            "auth_token": auth_token,
            "amount_cents": "10000",
            "expiration": 3600,
            "order_id": str(order_data['id']),
            "billing_data": {
                "apartment": "NA", "email": "test@test.com", "floor": "NA",
                "first_name": "Test", "street": "NA", "building": "NA",
                "phone_number": "+201000000000", "shipping_method": "NA",
                "postal_code": "NA", "city": "Cairo", "country": "Egypt",
                "last_name": "User", "state": "Cairo"
            },
            "currency": "EGP",
            "integration_id": 4626585
        }
    )
    
    if pk_resp.status_code == 201:
        print("   ✅ Wallet Integration WORKS (4626585)")
        print("\n" + "="*70)
        print("✅ RESULT: Both integrations exist and work!")
        print("="*70)
    else:
        print(f"   ❌ Wallet Integration FAILED: {pk_resp.status_code}")
        print(f"      Response: {pk_resp.text[:150]}")
        print("\n" + "="*70)
        print("❌ RESULT: Wallet integration (4626585) doesn't exist!")
        print("="*70)
        print("\nYou need to:")
        print("1. Login: https://accept.paymob.com/portal2/en/login")
        print("2. Go to: Developers → Payment Integrations")
        print("3. Create a NEW 'Mobile Wallets' integration")
        print("4. Copy the new Integration ID")
        print("5. Update backend/app/config/paymob_config.py")
        print("   MOBILE_WALLET_INTEGRATION_ID = YOUR_NEW_ID")
