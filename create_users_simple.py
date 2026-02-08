"""Create comprehensive test users for all roles - Simple Version"""
import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_test_users():
    """Create test users for each role"""

    # Connect to database
    conn = sqlite3.connect('gym_management.db')
    cursor = conn.cursor()

    print("=" * 70)
    print("CREATING TEST USERS FOR ALL ROLES")
    print("=" * 70)

    # Get existing branches
    cursor.execute("SELECT id, name FROM branches LIMIT 2")
    branches = cursor.fetchall()

    if not branches:
        print("❌ No branches found! Please create branches first.")
        conn.close()
        return

    branch1_id, branch1_name = branches[0]
    branch2_id, branch2_name = branches[1] if len(branches) > 1 else branches[0]

    print(f"\n📍 Using Branches:")
    print(f"   Branch 1: {branch1_name} (ID: {branch1_id})")
    print(f"   Branch 2: {branch2_name} (ID: {branch2_id})")

    # Define test users
    test_users = [
        # Owner
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
            'branch_id': branch1_id
        },
        {
            'username': 'manager2',
            'email': 'manager2@gym.com',
            'password': 'manager123',
            'role': 'branch_manager',
            'first_name': 'Sarah',
            'last_name': 'Wilson',
            'phone': '+1-555-0202',
            'branch_id': branch2_id
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
            'branch_id': branch1_id
        },
        {
            'username': 'reception2',
            'email': 'reception2@gym.com',
            'password': 'reception123',
            'role': 'receptionist',
            'first_name': 'Bob',
            'last_name': 'Smith',
            'phone': '+1-555-0302',
            'branch_id': branch2_id
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
            'branch_id': branch1_id
        },
        {
            'username': 'accountant2',
            'email': 'accountant2@gym.com',
            'password': 'accountant123',
            'role': 'accountant',
            'first_name': 'Diana',
            'last_name': 'Davis',
            'phone': '+1-555-0402',
            'branch_id': branch2_id
        },
    ]

    print("\n" + "=" * 70)
    print("CREATING USERS...")
    print("=" * 70 + "\n")

    created_count = 0
    skipped_count = 0

    for user_data in test_users:
        # Check if user already exists
        cursor.execute(
            "SELECT id FROM users WHERE username = ? OR email = ?",
            (user_data['username'], user_data['email'])
        )
        existing = cursor.fetchone()

        if existing:
            print(f"⏭️  SKIPPED: {user_data['username']} ({user_data['email']}) - Already exists")
            skipped_count += 1
            continue

        # Hash password
        password_hash = generate_password_hash(user_data['password'])

        # Insert user
        cursor.execute("""
            INSERT INTO users (
                username, email, password_hash, role, first_name, last_name,
                phone, branch_id, is_active, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_data['username'],
            user_data['email'],
            password_hash,
            user_data['role'],
            user_data['first_name'],
            user_data['last_name'],
            user_data['phone'],
            user_data['branch_id'],
            1,  # is_active
            datetime.utcnow().isoformat()
        ))

        created_count += 1

        branch_name = "No Branch"
        if user_data['branch_id']:
            if user_data['branch_id'] == branch1_id:
                branch_name = branch1_name
            elif user_data['branch_id'] == branch2_id:
                branch_name = branch2_name

        print(f"✅ CREATED: {user_data['first_name']} {user_data['last_name']}")
        print(f"   Username: {user_data['username']}")
        print(f"   Email: {user_data['email']}")
        print(f"   Password: {user_data['password']}")
        print(f"   Role: {user_data['role'].upper()}")
        print(f"   Branch: {branch_name}")
        print()

    # Commit changes
    conn.commit()

    print("=" * 70)
    print(f"✅ DATABASE COMMITTED SUCCESSFULLY")
    print(f"   Created: {created_count} users")
    print(f"   Skipped: {skipped_count} users (already exist)")
    print("=" * 70)

    # Print summary
    print("\n" + "=" * 70)
    print("📋 COMPLETE USER LIST FOR TESTING")
    print("=" * 70 + "\n")

    # Show owner accounts
    print("👑 OWNER ACCOUNTS:")
    cursor.execute("SELECT email, first_name, last_name FROM users WHERE role = 'owner'")
    owners = cursor.fetchall()
    for idx, (email, first_name, last_name) in enumerate(owners, 1):
        password = "zyad123" if "zyad" in email else "owner123"
        print(f"   {idx}. Email: {email} | Password: {password}")
        print(f"      Name: {first_name} {last_name}")
    print()

    # Show managers
    print("🎯 BRANCH MANAGER ACCOUNTS:")
    cursor.execute("""
        SELECT u.email, u.first_name, u.last_name, b.name
        FROM users u
        LEFT JOIN branches b ON u.branch_id = b.id
        WHERE u.role = 'branch_manager'
    """)
    managers = cursor.fetchall()
    for idx, (email, first_name, last_name, branch) in enumerate(managers, 1):
        print(f"   {idx}. Email: {email} | Password: manager123")
        print(f"      Name: {first_name} {last_name} | Branch: {branch or 'No Branch'}")
    print()

    # Show receptionists
    print("🎫 RECEPTIONIST ACCOUNTS:")
    cursor.execute("""
        SELECT u.email, u.first_name, u.last_name, b.name
        FROM users u
        LEFT JOIN branches b ON u.branch_id = b.id
        WHERE u.role = 'receptionist'
    """)
    receptionists = cursor.fetchall()
    for idx, (email, first_name, last_name, branch) in enumerate(receptionists, 1):
        print(f"   {idx}. Email: {email} | Password: reception123")
        print(f"      Name: {first_name} {last_name} | Branch: {branch or 'No Branch'}")
    print()

    # Show accountants
    print("💵 ACCOUNTANT ACCOUNTS:")
    cursor.execute("""
        SELECT u.email, u.first_name, u.last_name, b.name
        FROM users u
        LEFT JOIN branches b ON u.branch_id = b.id
        WHERE u.role = 'accountant'
    """)
    accountants = cursor.fetchall()
    for idx, (email, first_name, last_name, branch) in enumerate(accountants, 1):
        print(f"   {idx}. Email: {email} | Password: accountant123")
        print(f"      Name: {first_name} {last_name} | Branch: {branch or 'No Branch'}")
    print()

    print("=" * 70)
    print("✅ ALL TEST USERS CREATED SUCCESSFULLY!")
    print("=" * 70)
    print("\n💡 TIP: Use these credentials to test different role permissions\n")

    conn.close()

if __name__ == '__main__':
    create_test_users()
