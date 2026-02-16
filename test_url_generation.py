"""
Test what URL is actually being generated
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.config.paymob_config import PaymobConfig

# Test both URLs
test_token = "SAMPLE_TOKEN_ABC123"

card_url = PaymobConfig.get_iframe_url(test_token)
wallet_url = PaymobConfig.get_mobile_wallet_url(test_token)

print("="*70)
print("CHECKING URL GENERATION")
print("="*70)
print(f"\n📱 CARD URL:")
print(f"   {card_url}")
print(f"\n💰 WALLET URL:")
print(f"   {wallet_url}")
print(f"\n{'='*70}")
print("URLS ARE DIFFERENT?")
print("="*70)

if card_url == wallet_url:
    print("❌ PROBLEM: Both URLs are the SAME!")
    print("   Mobile wallet will show card form")
else:
    print("✅ GOOD: URLs are different")
    
if "/post_pay" in wallet_url:
    print("✅ GOOD: Wallet URL uses /post_pay (redirect)")
elif "/iframes/" in wallet_url:
    print("❌ PROBLEM: Wallet URL uses /iframes/ (wrong!)")
    print("   Should use /post_pay instead")

print("="*70)
