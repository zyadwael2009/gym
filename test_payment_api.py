"""Test payment creation"""
import requests
import json

# Backend URL
BASE_URL = "http://127.0.0.1:5000/api"

# Login as receptionist
login_data = {
    "username": "reception1@gym.com",
    "password": "reception123"
}

print("1. Logging in...")
response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
print(f"Login Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    token = data.get('access_token') or data.get('token')
    print(f"Token received: {token[:20] if token else 'None'}...")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Get subscriptions
    print("\n2. Getting subscriptions...")
    response = requests.get(f"{BASE_URL}/subscriptions", headers=headers)
    print(f"Subscriptions Status: {response.status_code}")

    if response.status_code == 200:
        subs_data = response.json()
        subscriptions = subs_data.get('subscriptions', [])
        print(f"Found {len(subscriptions)} subscriptions")

        if subscriptions:
            # Try to create a payment
            sub = subscriptions[0]
            customer_id = sub.get('customer', {}).get('id') or sub.get('customer_id')

            print(f"\n3. Creating payment for customer {customer_id}...")
            payment_data = {
                "customer_id": customer_id,
                "subscription_id": sub['id'],
                "amount": 100.0,
                "payment_method": "cash"
            }

            print(f"Payment data: {json.dumps(payment_data, indent=2)}")

            response = requests.post(f"{BASE_URL}/payments", json=payment_data, headers=headers)
            print(f"\nPayment Status: {response.status_code}")
            print(f"Response: {response.text[:500]}")

            if response.status_code in [200, 201]:
                print("✅ Payment created successfully!")
            else:
                print("❌ Payment creation failed!")
        else:
            print("No subscriptions found")
    else:
        print(f"Failed to get subscriptions: {response.text}")
else:
    print(f"Login failed: {response.text}")


