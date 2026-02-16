"""
Check if integration 4626585 already has an iFrame assigned
"""
import requests
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.config.paymob_config import PaymobConfig

print("="*70)
print("CHECKING YOUR PAYMOB ACCOUNT SETUP")
print("="*70)

# Get auth token
response = requests.post(
    "https://accept.paymob.com/api/auth/tokens",
    json={"api_key": PaymobConfig.API_KEY}
)

if response.status_code != 201:
    print(f"❌ Auth failed: {response.status_code}")
    exit()

auth_token = response.json()['token']
print("\n✅ Authenticated\n")

# Try to get merchant info
headers = {"Authorization": f"Bearer {auth_token}"}

print("Checking your integrations...")
print("-"*70)

# Method 1: Check if integration 4626585 has an iframe_id
try:
    # Get payment methods/integrations
    resp = requests.get(
        "https://accept.paymob.com/api/ecommerce/integrations",
        headers=headers
    )
    
    if resp.status_code == 200:
        data = resp.json()
        
        # Handle different response formats
        if isinstance(data, dict):
            integrations = data.get('integrations', [data])
        else:
            integrations = data
        
        print(f"\n📋 Found {len(integrations)} integration(s):\n")
        
        # First, let's see the raw structure
        print("DEBUG: Response structure:")
        print(type(data))
        if isinstance(data, list) and len(data) > 0:
            print(f"First item type: {type(data[0])}")
            print(f"First item: {data[0]}")
        elif isinstance(data, dict):
            print(f"Keys: {data.keys()}")
        print("-"*70)
        
        for integration in integrations:
            if isinstance(integration, str):
                print(f"String value: {integration}")
                continue
                
            int_id = integration.get('id') if hasattr(integration, 'get') else None
            int_type = integration.get('type', 'N/A') if hasattr(integration, 'get') else 'N/A'
            iframe_id = integration.get('iframe_id', 'N/A') if hasattr(integration, 'get') else 'N/A'
            is_active = integration.get('is_live', False) if hasattr(integration, 'get') else False
            
            print(f"Integration ID: {int_id}")
            print(f"  Type: {int_type}")
            print(f"  iFrame ID: {iframe_id}")
            print(f"  Status: {'Active' if is_active else 'Test Mode'}")
            
            if int_id == 4626585:
                print(f"  👆 THIS IS YOUR MOBILE WALLET INTEGRATION!")
                if iframe_id and iframe_id != 'N/A':
                    print(f"  ✅ It already has iFrame ID: {iframe_id}")
                    print(f"\n🎯 UPDATE YOUR CODE:")
                    print(f"     WALLET_IFRAME_ID = {iframe_id}")
                else:
                    print(f"  ⚠️  No iFrame assigned yet")
            
            if int_id == 4623557:
                print(f"  👆 THIS IS YOUR CARD INTEGRATION!")
                if iframe_id and iframe_id != 'N/A':
                    print(f"  ✅ It has iFrame ID: {iframe_id}")
            
            print()
        
    else:
        print(f"Could not fetch integrations: {resp.status_code}")
        
except Exception as e:
    print(f"Error checking integrations: {e}")

print("="*70)
print("IMPORTANT NOTES:")
print("="*70)
print("""
If integration 4626585 shows an iFrame ID:
  → Use that ID in your code (WALLET_IFRAME_ID = xxxxx)
  → No need to create anything!

If it shows 'N/A' or no iFrame:
  → Mobile wallet integration might not use iFrames
  → It might use direct redirect instead
  → See option below

If you're seeing "HTML/CSS/JS content" fields:
  → That's for CUSTOM iFrames (you don't need that!)
  → Look for standard iFrame options instead
  → Or contact Paymob support
""")

print("="*70)
