"""Test PaymobService directly"""
import sys
sys.path.insert(0, 'D:\\Programming\\Flutter\\gym\\backend')

from app.services.paymob_service import PaymobService

print("Testing PaymobService.initiate_payment()...")
print("="*60)

customer_data = {
    'first_name': 'Test',
    'last_name': 'Customer',
    'email': 'customer@test.com',
    'phone': '+201000000000'
}

try:
    result = PaymobService.initiate_payment(
        amount=500.0,
        customer_data=customer_data,
        subscription_id=None,
        payment_method='card'
    )
    
    print("\nResult:")
    print(result)
    
    if result:
        print("\n✓ SUCCESS!")
        print(f"Payment Token: {result.get('payment_token', '')[:30]}...")
        print(f"iFrame URL: {result.get('iframe_url', '')[:80]}...")
        print(f"Order ID: {result.get('order_id')}")
    else:
        print("\n✗ FAILED: No result returned")
        
except Exception as e:
    print(f"\n✗ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
