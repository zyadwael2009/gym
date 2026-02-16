"""Test mobile wallet URL format"""
import requests

# Test what happens with mobile wallet URL
token = "test_123"

print("Testing Paymob Mobile Wallet URL formats:")
print("="*60)

# Format 1: Payments/pay endpoint
url1 = f"https://accept.paymob.com/api/acceptance/payments/pay?payment_token={token}"
print(f"\n1. Payments/pay endpoint:")
print(f"   {url1}")

# Format 2: Mobile Wallets iframe (like card iframe)
url2 = f"https://accept.paymob.com/api/acceptance/iframes/859704?payment_token={token}"
print(f"\n2. iFrame endpoint (same as card):")
print(f"   {url2}")

# Format 3: Direct mobile wallet redirect
url3 = f"https://accept.paymobsolutions.com/api/acceptance/post_pay"
print(f"\n3. Post pay endpoint:")
print(f"   {url3}")

print("\n" + "="*60)
print("\nNOTE: Mobile wallets in Paymob typically use the SAME")
print("iFrame URL as cards, but with different integration_id")
print("The integration_id determines which payment method is shown")
