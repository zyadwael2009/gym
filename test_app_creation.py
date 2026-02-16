"""Test if app can be created with paymob blueprint"""
import sys
import traceback

print("="*60)
print("Testing App Creation with Paymob")
print("="*60)

try:
    print("\n1. Importing create_app...")
    from app import create_app
    print("[OK] create_app imported")
    
    print("\n2. Creating app instance...")
    app = create_app()
    print("[OK] App instance created")
    
    print("\n3. Listing registered routes...")
    paymob_routes = []
    for rule in app.url_map.iter_rules():
        if '/paymob' in str(rule):
            paymob_routes.append(str(rule))
            print(f"  {rule.methods} {rule}")
    
    if paymob_routes:
        print(f"\n[OK] Found {len(paymob_routes)} paymob routes")
    else:
        print("\n[ERROR] No paymob routes registered!")
        
except Exception as e:
    print(f"\n[ERROR] Failed: {e}")
    traceback.print_exc()
    sys.exit(1)
