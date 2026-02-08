"""Add test user to database"""
import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime

# Connect to database
conn = sqlite3.connect('gym_management.db')
cursor = conn.cursor()

# Create the new user
username = 'zyad'
email = 'z@gmail.com'
password = 'zyad123'
role = 'owner'  # 'owner' is the admin role in this system
first_name = 'Zyad'
last_name = 'Admin'
phone = '+1-555-0200'
is_active = 1
created_at = datetime.utcnow().isoformat()

# Hash the password
password_hash = generate_password_hash(password)

# Check if user already exists
cursor.execute("SELECT id FROM users WHERE email = ? OR username = ?", (email, username))
existing_user = cursor.fetchone()

if existing_user:
    # Update existing user
    cursor.execute("""
        UPDATE users
        SET password_hash = ?, role = ?, first_name = ?, last_name = ?, is_active = ?
        WHERE email = ? OR username = ?
    """, (password_hash, role, first_name, last_name, is_active, email, username))
    print(f"Updated existing user: {username}")
else:
    # Insert new user
    cursor.execute("""
        INSERT INTO users (username, email, password_hash, role, first_name, last_name, phone, is_active, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (username, email, password_hash, role, first_name, last_name, phone, is_active, created_at, created_at))
    print(f"Created new user: {username}")

# Commit changes
conn.commit()

# Verify the user was added
cursor.execute("SELECT id, username, email, role, first_name, last_name FROM users WHERE email = ?", (email,))
user = cursor.fetchone()

if user:
    print("\n=== USER CREATED SUCCESSFULLY ===")
    print(f"ID: {user[0]}")
    print(f"Username: {user[1]}")
    print(f"Email: {user[2]}")
    print(f"Role: {user[3]}")
    print(f"Name: {user[4]} {user[5]}")
    print(f"Password: zyad123")
    print("\nYou can now login with:")
    print(f"  Username: {user[1]}")
    print(f"  Password: zyad123")
else:
    print("ERROR: User was not created!")

conn.close()
