"""
Test actual API call to backend to see what URL it returns
"""
import requests
import json

# Your backend URL
BASE_URL = "http://192.168.1.6:5000"

# Test data (using customer_2 token from your tests)
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiY3VzdG9tZXJfMiIsInJvbGUiOiJjdXN0b21lciJ9.test_signature"
}

# Test WALLET payment
wallet_data = {
    "amount": 500,
    "payment_method": "wallet",  # Testing WALLET
    "plan_duration": 30,
    "plan_name": "Monthly Plan"
}

print("="*70)
print("TESTING BACKEND API - WALLET PAYMENT")
print("="*70)
print(f"\nSending request to: {BASE_URL}/api/paymob/initiate")
print(f"Payment method: wallet")
print(f"Amount: 500 EGP")
print("-"*70)

try:
    response = requests.post(
        f"{BASE_URL}/api/paymob/initiate",
        headers=headers,
        json=wallet_data,
        timeout=30
    )
    
    print(f"\n📡 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        if 'iframe_url' in data or 'payment_url' in data:
            url = data.get('iframe_url') or data.get('payment_url')
            print(f"\n✅ Payment initiated successfully!")
            print(f"\n🔗 Payment URL returned:")
            print(f"   {url}")
            print(f"\n{'='*70}")
            print("CHECKING URL TYPE:")
            print("="*70)
            
            if "/post_pay" in url:
                print("✅ CORRECT: Using /post_pay (wallet redirect)")
                print("   This should show wallet options!")
            elif "/iframes/" in url:
                print("❌ WRONG: Using /iframes/ (card form)")
                print("   This will show card fields instead of wallet!")
                print("\n⚠️  BACKEND NOT RESTARTED WITH NEW CODE!")
                print("   Please restart: python app.py")
            else:
                print(f"⚠️  Unknown URL format: {url}")
                
        else:
            print(f"\n❌ No payment URL in response:")
            print(json.dumps(data, indent=2))
    else:
        print(f"\n❌ Error response:")
        print(response.text[:500])
        
except requests.exceptions.ConnectionError:
    print("\n❌ Cannot connect to backend!")
    print("   Is backend running on http://192.168.1.6:5000?")
    print("   Start it with: python backend/app.py")
    
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "="*70)
