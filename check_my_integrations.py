"""Check what integrations exist in your Paymob account"""
import requests
import json

API_KEY = "ZXlKaGJHY2lPaUpJVXpVeE1pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SmpiR0Z6Y3lJNklrMWxjbU5vWVc1MElpd2ljSEp2Wm1sc1pWOXdheUk2T1RnNE5EWXpMQ0p1WVcxbElqb2lNVGN5TXpFd09UQTFPUzQyTlRFd09EWWlmUS5tdFNMa05GNnBxTTVmMVF5T0RiS0xiR21kb1FwOUZHZS1QcjdTVXhJbVp0N1htOWhnLThLNWdMN1BCSEJ0TXl5SUJnUlUwTm9fWF9vWGFOUF9INmFXUQ=="

print("="*70)
print("CHECKING YOUR PAYMOB INTEGRATIONS")
print("="*70)

# Step 1: Get auth token
print("\n1. Getting authentication token...")
try:
    response = requests.post(
        "https://accept.paymob.com/api/auth/tokens",
        json={"api_key": API_KEY},
        timeout=30
    )
    
    if response.status_code != 201:
        print(f"❌ Failed to authenticate: {response.status_code}")
        print(response.text)
        exit(1)
    
    data = response.json()
    auth_token = data.get('token')
    profile = data.get('profile', {})
    
    print(f"✅ Authenticated successfully")
    print(f"   Merchant: {profile.get('company_name', 'N/A')}")
    print(f"   Email: {profile.get('company_emails', ['N/A'])[0]}")
    print(f"   Merchant ID: {profile.get('id', 'N/A')}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Step 2: Try to get integrations (this endpoint might not exist in all Paymob versions)
print("\n2. Checking available payment methods...")
print("-"*70)

print("\n📋 YOUR CURRENT CONFIGURATION:")
print("-"*70)
print(f"Card Integration ID:   4623557")
print(f"Wallet Integration ID: 4626585")
print(f"iFrame ID:             859704")

print("\n\n⚠️  IMPORTANT: To verify these integrations exist:")
print("-"*70)
print("1. Login to Paymob Dashboard:")
print("   👉 https://accept.paymob.com/portal2/en/login")
print("")
print("2. Go to: Developers → Payment Integrations")
print("")
print("3. You should see:")
print("   ✓ Card/Online Card Payments → Copy its Integration ID")
print("   ✓ Mobile Wallets/E-Wallets → Copy its Integration ID")
print("")
print("4. If Mobile Wallets integration DOESN'T EXIST:")
print("   a. Click 'New Integration' or 'Add Integration'")
print("   b. Select 'Mobile Wallets' or 'E-Wallets'")
print("   c. Enable: Vodafone Cash, Orange Cash, Etisalat Cash")
print("   d. Save and copy the Integration ID")
print("")
print("5. Update backend/app/config/paymob_config.py with correct IDs")

print("\n\n🧪 TESTING YOUR CURRENT IDS:")
print("-"*70)

# Test creating an order with card integration
print("\n🔵 Testing CARD Integration (ID: 4623557)...")
try:
    order_response = requests.post(
        "https://accept.paymob.com/api/ecommerce/orders",
        json={
            "auth_token": auth_token,
            "delivery_needed": "false",
            "amount_cents": "10000",
            "currency": "EGP",
            "merchant_order_id": f"TEST-CARD-{int(requests.utils.default_user_agent())}",
            "items": []
        },
        timeout=30
    )
    
    if order_response.status_code == 201:
        order_data = order_response.json()
        order_id = order_data.get('id')
        print(f"   ✅ Order created: {order_id}")
        
        # Try to get payment key with card integration
        payment_key_response = requests.post(
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
                "integration_id": 4623557
            },
            timeout=30
        )
        
        if payment_key_response.status_code == 201:
            print(f"   ✅ Card Integration (4623557) is VALID and WORKING")
        else:
            print(f"   ❌ Card Integration Error: {payment_key_response.status_code}")
            print(f"      {payment_key_response.text[:200]}")
    else:
        print(f"   ❌ Failed to create order: {order_response.status_code}")
        
except Exception as e:
    print(f"   ❌ Error testing card: {e}")

# Test wallet integration
print("\n🟢 Testing WALLET Integration (ID: 4626585)...")
try:
    order_response = requests.post(
        "https://accept.paymob.com/api/ecommerce/orders",
        json={
            "auth_token": auth_token,
            "delivery_needed": "false",
            "amount_cents": "10000",
            "currency": "EGP",
            "merchant_order_id": f"TEST-WALLET-{int(requests.utils.default_user_agent())}",
            "items": []
        },
        timeout=30
    )
    
    if order_response.status_code == 201:
        order_data = order_response.json()
        order_id = order_data.get('id')
        print(f"   ✅ Order created: {order_id}")
        
        # Try to get payment key with wallet integration
        payment_key_response = requests.post(
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
                "integration_id": 4626585
            },
            timeout=30
        )
        
        if payment_key_response.status_code == 201:
            print(f"   ✅ Wallet Integration (4626585) is VALID and WORKING")
            print(f"   ✅ Both integrations are correctly configured!")
        else:
            print(f"   ❌ Wallet Integration Error: {payment_key_response.status_code}")
            print(f"      Response: {payment_key_response.text[:200]}")
            print(f"\n   ⚠️  This integration ID might not exist in your account!")
            print(f"      Please create it in Paymob Dashboard (see instructions above)")
    else:
        print(f"   ❌ Failed to create order: {order_response.status_code}")
        
except Exception as e:
    print(f"   ❌ Error testing wallet: {e}")

print("\n" + "="*70)
print("SUMMARY:")
print("="*70)
print("✓ If both tests passed: Your integrations are configured correctly")
print("✗ If wallet test failed: Create Mobile Wallet integration in dashboard")
print("\nNext steps: See PAYMOB_MOBILE_WALLET_SETUP.md for detailed instructions")
print("="*70)
