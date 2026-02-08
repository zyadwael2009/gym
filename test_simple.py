"""Simple dashboard test without emojis"""
import requests
import json

BASE_URL = "http://192.168.1.6:5000/api"

print("=" * 70)
print("TESTING DASHBOARD ENDPOINTS")
print("=" * 70)

# Step 1: Login
print("\n1. Testing Login...")
try:
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": "z@gmail.com", "password": "zyad123"},
        timeout=5
    )
    print(f"   Status: {login_response.status_code}")

    if login_response.status_code == 200:
        login_data = login_response.json()
        token = login_data.get('access_token')
        user = login_data.get('user', {})
        print(f"   [OK] Login successful")
        print(f"   User: {user.get('first_name')} {user.get('last_name')}")
        print(f"   Role: {user.get('role')}")
        print(f"   Token: {token[:30]}...")
    else:
        print(f"   [ERROR] Login failed: {login_response.text}")
        exit(1)
except Exception as e:
    print(f"   [ERROR] Error: {e}")
    exit(1)

# Step 2: Test Owner Dashboard
print("\n2. Testing Owner Dashboard...")
headers = {"Authorization": f"Bearer {token}"}
try:
    dashboard_response = requests.get(
        f"{BASE_URL}/dashboard/owner",
        headers=headers,
        timeout=5
    )
    print(f"   Status: {dashboard_response.status_code}")

    if dashboard_response.status_code == 200:
        data = dashboard_response.json()
        print(f"   [OK] Owner dashboard works")
        if 'summary' in data:
            print(f"   Summary keys: {list(data.get('summary', {}).keys())}")
    else:
        print(f"   [ERROR] Dashboard failed")
        print(f"   Response: {dashboard_response.text}")
except Exception as e:
    print(f"   [ERROR] Error: {e}")

print("\n" + "=" * 70)
print("CHECK BACKEND CONSOLE FOR JWT ERROR DETAILS")
print("=" * 70)
