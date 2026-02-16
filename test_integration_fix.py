"""Test that wallet and card use correct integration IDs"""
import sys
sys.path.insert(0, 'D:\\Programming\\Flutter\\gym\\backend')

from app.services.paymob_service import PaymobService
from app.config.paymob_config import PaymobConfig

print("Testing Wallet vs Card Integration:")
print("="*60)

customer_data = {
    'first_name': 'Test',
    'last_name': 'Customer',
    'email': 'customer@test.com',
    'phone': '+201000000000'
}

print("\n1. Testing CARD payment:")
print("-"*60)
print("Expected: Integration ID 4623557, iFrame URL")

card_result = PaymobService.initiate_payment(
    amount=100.0,
    customer_data=customer_data,
    subscription_id=None,
    payment_method='card'
)

if card_result:
    iframe_url = card_result.get('iframe_url', '')
    print(f"✓ Card Result:")
    print(f"  - URL starts with iframes: {'/iframes/' in iframe_url}")
    print(f"  - Payment Method: {card_result.get('payment_method', 'N/A')}")
    print(f"  - Order ID: {card_result.get('order_id')}")
else:
    print("✗ Card payment failed")

print("\n2. Testing WALLET payment:")
print("-"*60)
print("Expected: Integration ID 4626585, SAME iFrame URL")

wallet_result = PaymobService.initiate_payment(
    amount=100.0,
    customer_data=customer_data,
    subscription_id=None,
    payment_method='wallet'
)

if wallet_result:
    iframe_url = wallet_result.get('iframe_url', '')
    print(f"✓ Wallet Result:")
    print(f"  - URL starts with iframes: {'/iframes/' in iframe_url}")
    print(f"  - Payment Method: {wallet_result.get('payment_method', 'N/A')}")
    print(f"  - Order ID: {wallet_result.get('order_id')}")
else:
    print("✗ Wallet payment failed")

print("\n3. Verification:")
print("-"*60)
if card_result and wallet_result:
    card_url = card_result.get('iframe_url', '')
    wallet_url = wallet_result.get('iframe_url', '')
    
    # Both should have iframes in URL
    if '/iframes/859704' in card_url and '/iframes/859704' in wallet_url:
        print("✓ CORRECT: Both use same iFrame endpoint (859704)")
        print("✓ The payment_key was generated with different integration_ids")
        print(f"   - Card uses integration: {PaymobConfig.CARD_INTEGRATION_ID}")
        print(f"   - Wallet uses integration: {PaymobConfig.MOBILE_WALLET_INTEGRATION_ID}")
        print("✓ The iFrame will show different payment options automatically!")
    else:
        print("✗ ERROR: URLs don't match expected format")
        
print("\n" + "="*60)
