"""List all registered Flask routes"""
from app import create_app

app = create_app()

print("=" * 60)
print("Registered Flask Routes:")
print("=" * 60)

routes = []
for rule in app.url_map.iter_rules():
    routes.append({
        'endpoint': rule.endpoint,
        'methods': ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'})),
        'path': str(rule)
    })

# Sort by path
routes.sort(key=lambda x: x['path'])

# Filter for paymob routes
paymob_routes = [r for r in routes if 'paymob' in r['path'].lower()]

if paymob_routes:
    print("\n[OK] Paymob Routes Found:")
    for route in paymob_routes:
        print(f"  {route['methods']:10} {route['path']}")
else:
    print("\n[ERROR] No Paymob routes found!")
    print("\nAll API routes:")
    for route in routes:
        if '/api/' in route['path']:
            print(f"  {route['methods']:10} {route['path']}")
