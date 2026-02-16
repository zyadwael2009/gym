"""
Quick test script to verify Paymob backend integration Run this after starting the Flask server to test the payment initiation
"""

import requests
import json

# Configuration
BASE_URL = "http://192.168.1.6:5000"
TEST_CUSTOMER_EMAIL = "customer@test.com"
TEST_CUSTOMER_PASSWORD = "password123"

def test_paymob_integration():
    print("Testing Paymob Integration...")
    print("=" * 60)
    
    # Step 1: Login as customer
    print("\n1. Logging in as customer...")
    login_response = requests.post(
        f"{BASE_URL}/api/auth/customer/login",
        json={
            "email": TEST_CUSTOMER_EMAIL,
            "password": TEST_CUSTOMER_PASSWORD
        }
    )
    
    if login_response.status_code != 200:
        print(f"[ERROR] Login failed: {login_response.json()}")
        return
    
    login_data = login_response.json()
    token = login_data['access_token']
    customer_id = login_data['customer']['id']
    print(f"[OK] Login successful! Customer ID: {customer_id}")
    print(f"[DEBUG] Token: {token[:50]}...")
    
    # Step 2: Initiate payment
    print("\n2. Initiating payment...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"[DEBUG] Headers: {headers}")
    print(f"[DEBUG] Target URL: {BASE_URL}/api/paymob/initiate")
    
    payment_data = {
        "amount": 500.0,
        "plan_duration": 30,
        "plan_name": "Monthly Plan",
        "payment_method": "card"
    }
    
    payment_response = requests.post(
        f"{BASE_URL}/api/paymob/initiate",
        json=payment_data,
        headers=headers
    )
    
    print(f"\nStatus Code: {payment_response.status_code}")
    try:
        response_json = payment_response.json()
        print(f"Response: {json.dumps(response_json, indent=2)}")
    except:
        print(f"Response Text: {payment_response.text}")
    
    if payment_response.status_code in [200, 201]:
        response_data = payment_response.json()
        iframe_url = response_data.get('iframe_url')
        payment_id = response_data.get('payment_id')
        
        print(f"\n[OK] Payment initiated successfully!")
        print(f"Payment ID: {payment_id}")
        print(f"iFrame URL: {iframe_url[:80] if iframe_url else 'N/A'}...")
        print(f"\nOpen this URL in a browser to complete payment:")
        print(f"   {iframe_url}")
        
        # Step 3: Check payment status
        print("\n3. Checking payment status...")
        status_response = requests.get(
            f"{BASE_URL}/api/paymob/status/{payment_id}",
            headers=headers
        )
        
        print(f"Status: {json.dumps(status_response.json(), indent=2)}")
        
        return True
    else:
        print(f"[ERROR] Payment initiation failed")
        return False

if __name__ == "__main__":
    try:
        test_paymob_integration()
    except Exception as e:
        print(f"\n[ERROR] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
