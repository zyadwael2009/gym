"""
Test without auth - direct service call to check URL generation
"""
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.services.paymob_service import PaymobService

print("="*70)
print("TESTING PAYMOB SERVICE - WALLET PAYMENT")
print("="*70)

customer_data = {
    'first_name': 'Test',
    'last_name': 'Customer',
    'email': 'test@test.com',
    'phone': '+201000000000'
}

print("\n[1] Testing WALLET payment...")
print("-"*70)

wallet_result = PaymobService.initiate_payment(
    amount=500,
    customer_data=customer_data,
    subscription_id=None,
    payment_method='wallet'  # WALLET
)

if wallet_result:
    print(f"\n✅ Wallet payment initiated!")
    print(f"\n🔗 URL returned:")
    print(f"   {wallet_result['iframe_url']}")
    
    if '/post_pay' in wallet_result['iframe_url']:
        print(f"\n✅ CORRECT: Using /post_pay (wallet redirect)")
        print(f"   Should show: Vodafone Cash, Orange Cash, etc.")
    elif '/iframes/' in wallet_result['iframe_url']:
        print(f"\n❌ WRONG: Using /iframes/ (card form)")
        print(f"   Will show card fields instead!")
        print(f"\n⚠️  Issue: get_mobile_wallet_url() is not being used!")
else:
    print("\n❌ Failed to initiate wallet payment")

print("\n" + "="*70)
print("\n[2] Testing CARD payment (for comparison)...")
print("-"*70)

card_result = PaymobService.initiate_payment(
    amount=500,
    customer_data=customer_data,
    subscription_id=None,
    payment_method='card'  # CARD
)

if card_result:
    print(f"\n✅ Card payment initiated!")
    print(f"\n🔗 URL returned:")
    print(f"   {card_result['iframe_url']}")
    
    if '/iframes/' in card_result['iframe_url']:
        print(f"\n✅ CORRECT: Using /iframes/ (card iframe)")
    else:
        print(f"\n⚠️  Unexpected URL format")
else:
    print("\n❌ Failed to initiate card payment")

print("\n" + "="*70)
print("SUMMARY:")
print("="*70)

if wallet_result and card_result:
    wallet_url = wallet_result['iframe_url']
    card_url = card_result['iframe_url']
    
    if wallet_url == card_url:
        print("\n❌ PROBLEM: Wallet and Card use SAME URL!")
        print("   Both will show card form")
        print("\n🔧 Solution: Check paymob_service.py line 189-195")
    else:
        print("\n✅ GOOD: Wallet and Card use DIFFERENT URLs!")
        print("\nWallet URL should have: /post_pay")
        print("Card URL should have: /iframes/")

print("\n" + "="*70)
