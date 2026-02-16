from app import create_app
from app.database import db
from app.models.user import User

app = create_app()
app.app_context().push()

print("\n" + "="*60)
print("        ALL USERS WITH PASSWORD VERIFICATION")
print("="*60 + "\n")

# Test passwords
test_passwords = {
    'owner': 'password123',
    'zyad': 'zyad123',
    'admin': 'admin123',
    'manager': 'password123',
    'receptionist': 'password123',
    'accountant': 'accountant123',
    'customer': 'password123'
}

users = User.query.all()

for user in users:
    print(f"👤 Username: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   Role: {user.role}")
    print(f"   Branch ID: {user.branch_id}")
    print(f"   Active: {user.is_active}")
    
    # Try to find the correct password
    password_found = False
    for test_pwd in ['password123', 'zyad123', 'admin123', 'manager123', 
                     'reception123', 'accountant123', 'test123', '123456']:
        if user.check_password(test_pwd):
            print(f"   ✅ PASSWORD: {test_pwd}")
            password_found = True
            break
    
    if not password_found:
        print(f"   ❌ PASSWORD: Unknown (try: password123)")
    
    print("-" * 60 + "\n")

print("\n" + "="*60)
print("           RECOMMENDED LOGIN CREDENTIALS")
print("="*60 + "\n")

print("For OWNER role:")
print("  Username: owner")
print("  Password: password123")
print()
print("For BRANCH MANAGER role:")
print("  Username: manager")
print("  Password: password123")
print()
print("For RECEPTIONIST role:")
print("  Username: receptionist")
print("  Password: password123")
print()
print("For ACCOUNTANT role:")
print("  Username: accountant")
print("  Password: password123")
print()
