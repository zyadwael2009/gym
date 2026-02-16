"""Test mobile wallet vs card payment URLs"""
import sys
sys.path.insert(0, 'D:\\Programming\\Flutter\\gym\\backend')

from app.services.paymob_service import PaymobService

print("Testing Payment URL Generation...")
print("="*60)

customer_data = {
    'first_name': 'Test',
    'last_name': 'Customer',
    'email': 'customer@test.com',
    'phone': '+201000000000'
}

# Test 1: Card Payment
print("\n1. Testing CARD payment:")
print("-"*60)
card_result = PaymobService.initiate_payment(
    amount=500.0,
    customer_data=customer_data,
    subscription_id=None,
    payment_method='card'
)

if card_result:
    print(f"✓ Card Payment Initiated")
    print(f"  Payment Method: {card_result.get('payment_method', 'N/A')}")
    print(f"  Order ID: {card_result.get('order_id')}")
    print(f"  URL Type: {'iFrame' if '/iframes/' in card_result.get('iframe_url', '') else 'Redirect'}")
    print(f"  URL: {card_result.get('iframe_url', '')[:100]}...")
else:
    print("✗ Card payment failed")

# Test 2: Mobile Wallet Payment
print("\n2. Testing MOBILE WALLET payment:")
print("-"*60)
wallet_result = PaymobService.initiate_payment(
    amount=500.0,
    customer_data=customer_data,
    subscription_id=None,
    payment_method='wallet'
)

if wallet_result:
    print(f"✓ Mobile Wallet Payment Initiated")
    print(f"  Payment Method: {wallet_result.get('payment_method', 'N/A')}")
    print(f"  Order ID: {wallet_result.get('order_id')}")
    print(f"  URL Type: {'Mobile Wallet' if '/payments/pay' in wallet_result.get('iframe_url', '') else 'iFrame'}")
    print(f"  URL: {wallet_result.get('iframe_url', '')[:100]}...")
else:
    print("✗ Mobile wallet payment failed")

# Compare URLs
print("\n3. URL Comparison:")
print("-"*60)
if card_result and wallet_result:
    card_url = card_result.get('iframe_url', '')
    wallet_url = wallet_result.get('iframe_url', '')
    
    if '/iframes/' in card_url and '/payments/pay' in wallet_url:
        print("✓ CORRECT: Card uses iFrame, Wallet uses payment redirect")
    elif card_url == wallet_url:
        print("✗ ERROR: Both methods use the same URL!")
    else:
        print("⚠ WARNING: Unexpected URL patterns")
        
print("\n" + "="*60)
