"""Final test - API endpoints with string identity fix"""
import requests
import json
import sys

BASE_URL = "http://192.168.1.6:5000/api"

print("Testing Dashboard API with JWT String Identity Fix")
print("=" * 70)

try:
    # Login
    print("\n1. Login...")
    login_resp = requests.post(f"{BASE_URL}/auth/login",
                               json={"username": "z@gmail.com", "password": "zyad123"},
                               timeout=5)

    if login_resp.status_code != 200:
        print(f"   Login failed: {login_resp.status_code}")
        print(f"   Response: {login_resp.text}")
        sys.exit(1)

    data = login_resp.json()
    token = data.get('access_token')
    print(f"   Login SUCCESS!")
    print(f"   User: {data.get('user', {}).get('username')}")

    # Test dashboard
    print("\n2. Testing /api/dashboard/owner...")
    headers = {'Authorization': f'Bearer {token}'}
    dash_resp = requests.get(f"{BASE_URL}/dashboard/owner",
                             headers=headers,
                             timeout=5)

    print(f"   Status: {dash_resp.status_code}")

    if dash_resp.status_code == 200:
        print(f"   SUCCESS! Dashboard works!")
        dash_data = dash_resp.json()
        if 'summary' in dash_data:
            summary = dash_data['summary']
            print(f"   Revenue: ${summary.get('total_revenue', 0)}")
            print(f"   Customers: {summary.get('new_customers', 0)}")
            print(f"   Subscriptions: {summary.get('active_subscriptions', 0)}")
        print("\n" + "=" * 70)
        print("DASHBOARD FIX: SUCCESS!")
        print("=" * 70)
    else:
        print(f"   FAILED: {dash_resp.text}")
        print("\n" + "=" * 70)
        print("DASHBOARD FIX: FAILED")
        print("=" * 70)

except Exception as e:
    print(f"\nError: {e}")
    print("Make sure backend is running on http://192.168.1.6:5000")
