"""Create comprehensive test users for all roles"""
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import from app.py (not the app package)
import app as app_module
from app.database import db
from app.models.user import User
from app.models.branch import Branch
from datetime import datetime

def create_test_users():
    """Create test users for each role"""

    app = app_module.create_app()

    with app.app_context():
        print("=" * 70)
        print("CREATING TEST USERS FOR ALL ROLES")
        print("=" * 70)

        # Get existing branches
        branches = Branch.query.all()
        if not branches:
            print("❌ No branches found! Please create branches first.")
            return

        branch1 = branches[0]
        branch2 = branches[1] if len(branches) > 1 else branch1

        print(f"\n📍 Using Branches:")
        print(f"   Branch 1: {branch1.name} (ID: {branch1.id})")
        print(f"   Branch 2: {branch2.name} (ID: {branch2.id})")

        # Define test users
        test_users = [
            # Owner (already exists as zyad@gmail.com)
            {
                'username': 'owner',
                'email': 'owner@gym.com',
                'password': 'owner123',
                'role': 'owner',
                'first_name': 'System',
                'last_name': 'Owner',
                'phone': '+1-555-0100',
                'branch_id': None
            },

            # Branch Managers
            {
                'username': 'manager1',
                'email': 'manager1@gym.com',
                'password': 'manager123',
                'role': 'branch_manager',
                'first_name': 'John',
                'last_name': 'Manager',
                'phone': '+1-555-0201',
                'branch_id': branch1.id
            },
            {
                'username': 'manager2',
                'email': 'manager2@gym.com',
                'password': 'manager123',
                'role': 'branch_manager',
                'first_name': 'Sarah',
                'last_name': 'Wilson',
                'phone': '+1-555-0202',
                'branch_id': branch2.id
            },

            # Receptionists
            {
                'username': 'reception1',
                'email': 'reception1@gym.com',
                'password': 'reception123',
                'role': 'receptionist',
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'phone': '+1-555-0301',
                'branch_id': branch1.id
            },
            {
                'username': 'reception2',
                'email': 'reception2@gym.com',
                'password': 'reception123',
                'role': 'receptionist',
                'first_name': 'Bob',
                'last_name': 'Smith',
                'phone': '+1-555-0302',
                'branch_id': branch2.id
            },

            # Accountants
            {
                'username': 'accountant1',
                'email': 'accountant1@gym.com',
                'password': 'accountant123',
                'role': 'accountant',
                'first_name': 'Charlie',
                'last_name': 'Brown',
                'phone': '+1-555-0401',
                'branch_id': branch1.id
            },
            {
                'username': 'accountant2',
                'email': 'accountant2@gym.com',
                'password': 'accountant123',
                'role': 'accountant',
                'first_name': 'Diana',
                'last_name': 'Davis',
                'phone': '+1-555-0402',
                'branch_id': branch2.id
            },
        ]

        print("\n" + "=" * 70)
        print("CREATING USERS...")
        print("=" * 70 + "\n")

        created_count = 0
        skipped_count = 0

        for user_data in test_users:
            # Check if user already exists
            existing_user = User.query.filter(
                (User.username == user_data['username']) |
                (User.email == user_data['email'])
            ).first()

            if existing_user:
                print(f"⏭️  SKIPPED: {user_data['username']} ({user_data['email']}) - Already exists")
                skipped_count += 1
                continue

            # Create new user
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                role=user_data['role'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                phone=user_data['phone'],
                branch_id=user_data['branch_id'],
                is_active=True,
                created_at=datetime.utcnow()
            )
            user.set_password(user_data['password'])

            db.session.add(user)
            created_count += 1

            branch_name = "No Branch"
            if user_data['branch_id']:
                branch_obj = Branch.query.get(user_data['branch_id'])
                branch_name = branch_obj.name if branch_obj else "Unknown"

            print(f"✅ CREATED: {user_data['first_name']} {user_data['last_name']}")
            print(f"   Username: {user_data['username']}")
            print(f"   Email: {user_data['email']}")
            print(f"   Password: {user_data['password']}")
            print(f"   Role: {user_data['role'].upper()}")
            print(f"   Branch: {branch_name}")
            print()

        # Commit all changes
        try:
            db.session.commit()
            print("=" * 70)
            print(f"✅ DATABASE COMMITTED SUCCESSFULLY")
            print(f"   Created: {created_count} users")
            print(f"   Skipped: {skipped_count} users (already exist)")
            print("=" * 70)
        except Exception as e:
            db.session.rollback()
            print(f"❌ ERROR: {e}")
            print("=" * 70)
            return

        # Print summary
        print("\n" + "=" * 70)
        print("📋 COMPLETE USER LIST FOR TESTING")
        print("=" * 70 + "\n")

        # Show the zyad admin user too
        zyad_user = User.query.filter_by(email='zyad@gmail.com').first()
        if zyad_user:
            print("👑 OWNER ACCOUNTS:")
            print(f"   1. Email: zyad@gmail.com | Password: zyad123 | Name: Zyad")
            print(f"   2. Email: owner@gym.com | Password: owner123 | Name: System Owner")
            print()

        print("🎯 BRANCH MANAGER ACCOUNTS:")
        managers = User.query.filter_by(role='branch_manager').all()
        for idx, mgr in enumerate(managers, 1):
            branch_name = mgr.branch.name if mgr.branch else "No Branch"
            print(f"   {idx}. Email: {mgr.email} | Password: manager123")
            print(f"      Name: {mgr.first_name} {mgr.last_name} | Branch: {branch_name}")
        print()

        print("🎫 RECEPTIONIST ACCOUNTS:")
        receptionists = User.query.filter_by(role='receptionist').all()
        for idx, rec in enumerate(receptionists, 1):
            branch_name = rec.branch.name if rec.branch else "No Branch"
            print(f"   {idx}. Email: {rec.email} | Password: reception123")
            print(f"      Name: {rec.first_name} {rec.last_name} | Branch: {branch_name}")
        print()

        print("💵 ACCOUNTANT ACCOUNTS:")
        accountants = User.query.filter_by(role='accountant').all()
        for idx, acc in enumerate(accountants, 1):
            branch_name = acc.branch.name if acc.branch else "No Branch"
            print(f"   {idx}. Email: {acc.email} | Password: accountant123")
            print(f"      Name: {acc.first_name} {acc.last_name} | Branch: {branch_name}")
        print()

        print("=" * 70)
        print("✅ ALL TEST USERS CREATED SUCCESSFULLY!")
        print("=" * 70)
        print("\n💡 TIP: Use these credentials to test different role permissions\n")

if __name__ == '__main__':
    create_test_users()
