"""Create test users for all roles"""
import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime

# Connect to database
conn = sqlite3.connect('gym_management.db')
cursor = conn.cursor()

# Get branch IDs
cursor.execute("SELECT id FROM branches LIMIT 2")
branches = cursor.fetchall()
branch1_id = branches[0][0] if branches else None
branch2_id = branches[1][0] if len(branches) > 1 else branch1_id

# Users to create
users = [
    # Owner (already exists as zyad)
    {
        'username': 'admin',
        'email': 'admin@gym.com',
        'password': 'admin123',
        'role': 'owner',
        'first_name': 'System',
        'last_name': 'Admin',
        'phone': '+1-555-0001',
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
        'phone': '+1-555-0002',
        'branch_id': branch1_id
    },
    {
        'username': 'manager2',
        'email': 'manager2@gym.com',
        'password': 'manager123',
        'role': 'branch_manager',
        'first_name': 'Sarah',
        'last_name': 'Manager',
        'phone': '+1-555-0003',
        'branch_id': branch2_id
    },
    # Receptionists
    {
        'username': 'reception1',
        'email': 'reception1@gym.com',
        'password': 'reception123',
        'role': 'receptionist',
        'first_name': 'Alice',
        'last_name': 'Reception',
        'phone': '+1-555-0004',
        'branch_id': branch1_id
    },
    {
        'username': 'reception2',
        'email': 'reception2@gym.com',
        'password': 'reception123',
        'role': 'receptionist',
        'first_name': 'Bob',
        'last_name': 'Reception',
        'phone': '+1-555-0005',
        'branch_id': branch2_id
    },
    # Accountants
    {
        'username': 'accountant1',
        'email': 'accountant1@gym.com',
        'password': 'accountant123',
        'role': 'accountant',
        'first_name': 'Charlie',
        'last_name': 'Accountant',
        'phone': '+1-555-0006',
        'branch_id': branch1_id
    },
    {
        'username': 'accountant2',
        'email': 'accountant2@gym.com',
        'password': 'accountant123',
        'role': 'accountant',
        'first_name': 'Diana',
        'last_name': 'Accountant',
        'phone': '+1-555-0007',
        'branch_id': branch2_id
    },
]

print("=" * 60)
print("CREATING TEST USERS FOR ALL ROLES")
print("=" * 60)

created_users = []

for user_data in users:
    username = user_data['username']

    # Check if user exists
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    existing = cursor.fetchone()

    if existing:
        # Update password
        password_hash = generate_password_hash(user_data['password'])
        cursor.execute("""
            UPDATE users
            SET password_hash = ?, email = ?, role = ?, first_name = ?,
                last_name = ?, phone = ?, branch_id = ?, is_active = 1
            WHERE username = ?
        """, (
            password_hash,
            user_data['email'],
            user_data['role'],
            user_data['first_name'],
            user_data['last_name'],
            user_data['phone'],
            user_data['branch_id'],
            username
        ))
        print(f"✅ Updated: {username}")
    else:
        # Create new user
        password_hash = generate_password_hash(user_data['password'])
        created_at = datetime.utcnow().isoformat()

        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, first_name,
                             last_name, phone, is_active, branch_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            username,
            user_data['email'],
            password_hash,
            user_data['role'],
            user_data['first_name'],
            user_data['last_name'],
            user_data['phone'],
            1,
            user_data['branch_id'],
            created_at,
            created_at
        ))
        print(f"✅ Created: {username}")

    created_users.append(user_data)

conn.commit()

print("\n" + "=" * 60)
print("✅ ALL USERS CREATED SUCCESSFULLY!")
print("=" * 60)
print("\n📋 LOGIN CREDENTIALS:\n")

print("🔴 OWNER (Full Access):")
print("   Username: zyad         | Password: zyad123")
print("   Username: admin        | Password: admin123")

print("\n🔵 BRANCH MANAGERS:")
print("   Username: manager1     | Password: manager123 (Branch 1)")
print("   Username: manager2     | Password: manager123 (Branch 2)")

print("\n🟢 RECEPTIONISTS:")
print("   Username: reception1   | Password: reception123 (Branch 1)")
print("   Username: reception2   | Password: reception123 (Branch 2)")

print("\n🟡 ACCOUNTANTS:")
print("   Username: accountant1  | Password: accountant123 (Branch 1)")
print("   Username: accountant2  | Password: accountant123 (Branch 2)")

print("\n" + "=" * 60)

# Save to file
with open('ALL_USER_CREDENTIALS.txt', 'w') as f:
    f.write("=" * 60 + "\n")
    f.write("GYM MANAGEMENT SYSTEM - ALL USER CREDENTIALS\n")
    f.write("=" * 60 + "\n\n")

    f.write("OWNER (Full Access):\n")
    f.write("  Username: zyad         | Password: zyad123\n")
    f.write("  Username: admin        | Password: admin123\n\n")

    f.write("BRANCH MANAGERS:\n")
    f.write("  Username: manager1     | Password: manager123 (Branch 1)\n")
    f.write("  Username: manager2     | Password: manager123 (Branch 2)\n\n")

    f.write("RECEPTIONISTS:\n")
    f.write("  Username: reception1   | Password: reception123 (Branch 1)\n")
    f.write("  Username: reception2   | Password: reception123 (Branch 2)\n\n")

    f.write("ACCOUNTANTS:\n")
    f.write("  Username: accountant1  | Password: accountant123 (Branch 1)\n")
    f.write("  Username: accountant2  | Password: accountant123 (Branch 2)\n\n")

print("💾 Credentials saved to: ALL_USER_CREDENTIALS.txt")
print("=" * 60)

conn.close()
