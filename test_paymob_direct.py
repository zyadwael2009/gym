"""Direct test of Paymob API"""
import requests
import sys

API_KEY = "ZXlKaGJHY2lPaUpJVXpVeE1pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SmpiR0Z6Y3lJNklrMWxjbU5vWVc1MElpd2ljSEp2Wm1sc1pWOXdheUk2T1RnNE5EWXpMQ0p1WVcxbElqb2lNVGN5TXpFd09UQTFPUzQyTlRFd09EWWlmUS5tdFNMa05GNnBxTTVmMVF5T0RiS0xiR21kb1FwOUZHZS1QcjdTVXhJbVp0N1htOWhnLThLNWdMN1BCSEJ0TXl5SUJnUlUwTm9fWF9vWGFOUF9INmFXUQ=="

print("Testing Paymob API directly...")
print("="*60)

# Step 1: Get auth token
print("\n1. Getting authentication token...")
print(f"URL: https://accept.paymob.com/api/auth/tokens")
print(f"API Key (first 30 chars): {API_KEY[:30]}...")

try:
    response = requests.post(
        "https://accept.paymob.com/api/auth/tokens",
        json={"api_key": API_KEY},
        timeout=30
    )
    
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"\nResponse Body:")
    print(response.text)
    
    if response.status_code == 200 or response.status_code == 201:
        data = response.json()
        if 'token' in data:
            print(f"\n✓ SUCCESS! Auth token received: {data['token'][:30]}...")
            auth_token = data['token']
            
            # Step 2: Try to create an order
            print("\n" + "="*60)
            print("2. Creating test order...")
            order_response = requests.post(
                "https://accept.paymob.com/api/ecommerce/orders",
                json={
                    "auth_token": auth_token,
                    "delivery_needed": "false",
                    "amount_cents": "50000",
                    "currency": "EGP",
                    "merchant_order_id": "TEST-123456",
                    "items": []
                },
                timeout=30
            )
            
            print(f"Order Response Status: {order_response.status_code}")
            print(f"Order Response:")
            print(order_response.text)
            
        else:
            print("\n✗ ERROR: No token in response!")
    else:
        print(f"\n✗ ERROR: Authentication failed!")
        try:
            error_data = response.json()
            print(f"Error details: {error_data}")
        except:
            pass
            
except requests.exceptions.Timeout:
    print("\n✗ ERROR: Request timeout!")
except requests.exceptions.ConnectionError as e:
    print(f"\n✗ ERROR: Connection failed: {e}")
except Exception as e:
    print(f"\n✗ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
