from app import create_app
from app.database import db
from app.models.user import User

app = create_app()
app.app_context().push()

print("\n" + "="*70)
print("           CURRENT USERS IN DATABASE")
print("="*70 + "\n")

users = User.query.all()

for user in users:
    print(f"ID: {user.id}")
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")
    print(f"Role: {user.role}")
    print(f"Branch ID: {user.branch_id}")
    print(f"Active: {user.is_active}")
    print("-" * 70)

print("\n" + "="*70)
print("        TRY THESE LOGIN CREDENTIALS FOR EMPLOYEE APP")
print("="*70 + "\n")

print("🔴 OWNER (Full Access):")
print("   Username: owner")
print("   Password: password123")
print()

print("🔵 BRANCH MANAGER:")
print("   Username: manager")
print("   Password: password123")
print()

print("🟢 RECEPTIONIST:")
print("   Username: receptionist")
print("   Password: password123")
print()

print("🟡 ACCOUNTANT:")
print("   Username: accountant")
print("   Password: password123")
print()

print("="*70)
print("Note: If these don't work, run: python create_test_users.py")
print("="*70 + "\n")
