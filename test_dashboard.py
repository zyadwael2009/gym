"""Test dashboard endpoints"""
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
        print(f"   ✅ Login successful")
        print(f"   User: {user.get('first_name')} {user.get('last_name')}")
        print(f"   Role: {user.get('role')}")
        print(f"   Token: {token[:30]}...")
    else:
        print(f"   ❌ Login failed: {login_response.text}")
        exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    print(f"\n⚠️  Cannot connect to backend at {BASE_URL}")
    print(f"   Make sure:")
    print(f"   1. Backend is running (python app.py)")
    print(f"   2. Backend is listening on 0.0.0.0:5000")
    print(f"   3. Firewall allows port 5000")
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
        print(f"   ✅ Owner dashboard works")
        print(f"   Summary: {json.dumps(data.get('summary', {}), indent=6)}")
    else:
        print(f"   ❌ Dashboard failed: {dashboard_response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Step 3: Test Manager Dashboard (should fail for owner)
print("\n3. Testing Manager Dashboard...")
try:
    manager_response = requests.get(
        f"{BASE_URL}/dashboard/manager",
        headers=headers,
        timeout=5
    )
    print(f"   Status: {manager_response.status_code}")
    print(f"   Response: {manager_response.text[:200]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Step 4: Test Staff Dashboard (should fail for owner)
print("\n4. Testing Staff Dashboard...")
try:
    staff_response = requests.get(
        f"{BASE_URL}/dashboard/staff",
        headers=headers,
        timeout=5
    )
    print(f"   Status: {staff_response.status_code}")
    print(f"   Response: {staff_response.text[:200]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Step 5: Test with Manager Account
print("\n5. Testing with Manager Account...")
try:
    manager_login = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": "manager1@gym.com", "password": "manager123"},
        timeout=5
    )

    if manager_login.status_code == 200:
        manager_token = manager_login.json().get('access_token')
        manager_headers = {"Authorization": f"Bearer {manager_token}"}

        manager_dash = requests.get(
            f"{BASE_URL}/dashboard/manager",
            headers=manager_headers,
            timeout=5
        )
        print(f"   Status: {manager_dash.status_code}")

        if manager_dash.status_code == 200:
            print(f"   ✅ Manager dashboard works")
            data = manager_dash.json()
            if 'summary' in data:
                print(f"   Summary: {json.dumps(data.get('summary', {}), indent=6)}")
            elif 'financial' in data:
                print(f"   Financial: {json.dumps(data.get('financial', {}), indent=6)}")
        else:
            print(f"   ❌ Manager dashboard failed: {manager_dash.text}")
    else:
        print(f"   ❌ Manager login failed")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
