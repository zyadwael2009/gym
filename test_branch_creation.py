"""Test branch creation API"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

# Login as owner
print("1. Logging in as owner...")
login_response = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "owner@gym.com",
    "password": "owner123"
})

print(f"Login status: {login_response.status_code}")

if login_response.status_code == 200:
    data = login_response.json()
    token = data.get('access_token')
    print(f"✓ Logged in successfully")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Try to create a branch
    print("\n2. Creating branch...")
    branch_data = {
        "name": "Test Branch API",
        "code": "TESTAPI",
        "address_line1": "123 Test Street",
        "phone": "1234567890",
        "email": "testapi@gym.com",
        "monthly_target": 50000,
        "is_active": True
    }

    print(f"Request data: {json.dumps(branch_data, indent=2)}")

    create_response = requests.post(
        f"{BASE_URL}/branches",
        json=branch_data,
        headers=headers
    )

    print(f"\nResponse status: {create_response.status_code}")
    print(f"Response body: {create_response.text[:500]}")

    if create_response.status_code in [200, 201]:
        print("\n✓ Branch created successfully!")
        result = create_response.json()
        print(f"Branch ID: {result.get('branch', {}).get('id')}")
    else:
        print("\n✗ Branch creation failed!")
        try:
            error = create_response.json()
            print(f"Error: {error.get('error')}")
        except:
            print(f"Raw response: {create_response.text}")
else:
    print(f"✗ Login failed: {login_response.text}")

