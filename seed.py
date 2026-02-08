"""
Database Seed Script
====================
This script erases the existing database and creates fresh test data
including users for all roles: owner, branch_manager, receptionist, accountant, and customer
"""

from datetime import datetime, date, time
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from config import Config
from app.database import db
from app.models.user import User
from app.models.branch import Branch
from app.models.customer import Customer
from app.models.subscription import Subscription
from app.models.payment import Payment
from app.models.attendance import Attendance
from app.models.complaint import Complaint

def reset_database():
    """Drop all tables and recreate them"""
    print("🗑️  Dropping all tables...")
    db.drop_all()
    print("✅ All tables dropped")

    print("🏗️  Creating fresh tables...")
    db.create_all()
    print("✅ All tables created")

def create_test_users():
    """Create test users for all roles"""
    print("\n👥 Creating test users...")

    users_data = []

    # 1. Owner (Central Admin)
    owner = User(
        username='owner',
        email='owner@gym.com',
        first_name='Admin',
        last_name='Owner',
        phone='+20 100 000 0001',
        role='owner',
        is_active=True
    )
    owner.set_password('owner123')
    users_data.append(('👑 Owner', owner))

    # 2. Branch Manager
    manager = User(
        username='manager',
        email='manager@gym.com',
        first_name='Branch',
        last_name='Manager',
        phone='+20 100 000 0002',
        role='branch_manager',
        is_active=True
    )
    manager.set_password('manager123')
    users_data.append(('🏢 Branch Manager', manager))

    # 3. Receptionist (Front Desk)
    receptionist = User(
        username='receptionist',
        email='receptionist@gym.com',
        first_name='Front',
        last_name='Desk',
        phone='+20 100 000 0003',
        role='receptionist',
        is_active=True
    )
    receptionist.set_password('receptionist123')
    users_data.append(('🎫 Receptionist', receptionist))

    # 4. Accountant
    accountant = User(
        username='accountant',
        email='accountant@gym.com',
        first_name='Finance',
        last_name='Manager',
        phone='+20 100 000 0004',
        role='accountant',
        is_active=True
    )
    accountant.set_password('accountant123')
    users_data.append(('💰 Accountant', accountant))

    # 5. Customer
    customer_user = User(
        username='customer',
        email='customer@gym.com',
        first_name='John',
        last_name='Doe',
        phone='+20 100 000 0005',
        role='customer',
        is_active=True
    )
    customer_user.set_password('customer123')
    users_data.append(('🏋️ Customer', customer_user))

    # Add all users to session
    for label, user in users_data:
        db.session.add(user)

    # Commit users first
    db.session.commit()
    print("✅ All users created successfully")

    return {
        'owner': owner,
        'manager': manager,
        'receptionist': receptionist,
        'accountant': accountant,
        'customer_user': customer_user
    }

def create_test_branches(users):
    """Create test branches"""
    print("\n🏢 Creating test branches...")

    branches = []

    # Main Branch
    main_branch = Branch(
        name='Main Branch - Downtown',
        code='MAIN001',
        address_line1='123 Main Street',
        address_line2='Downtown District',
        city='Cairo',
        state='Cairo Governorate',
        pincode='11511',
        country='Egypt',
        phone='+20 2 1234 5678',
        email='main@gym.com',
        opening_time=time(6, 0),
        closing_time=time(22, 0),
        monthly_target=100000.00,
        manager_id=users['manager'].id,
        is_active=True
    )
    branches.append(main_branch)

    # Second Branch
    second_branch = Branch(
        name='North Branch - Nasr City',
        code='NORTH01',
        address_line1='456 El Nasr Road',
        address_line2='Nasr City',
        city='Cairo',
        state='Cairo Governorate',
        pincode='11371',
        country='Egypt',
        phone='+20 2 8765 4321',
        email='north@gym.com',
        opening_time=time(6, 0),
        closing_time=time(22, 0),
        monthly_target=80000.00,
        is_active=True
    )
    branches.append(second_branch)

    # Add branches
    for branch in branches:
        db.session.add(branch)

    db.session.commit()

    # Update user branch assignments
    users['manager'].branch_id = main_branch.id
    users['receptionist'].branch_id = main_branch.id
    users['accountant'].branch_id = main_branch.id
    users['customer_user'].branch_id = main_branch.id

    db.session.commit()

    print(f"✅ Created {len(branches)} branches")
    return {'main_branch': main_branch, 'second_branch': second_branch}

def create_test_customer_profile(customer_user, branch):
    """Create customer profile with health data"""
    print("\n🏋️ Creating customer profile...")

    customer = Customer(
        user_id=customer_user.id,
        branch_id=branch.id,
        member_id='MEM-2026-001',
        date_of_birth=date(1990, 1, 15),
        gender='male',
        height_cm=175.0,
        weight_kg=80.0,
        emergency_contact_name='Jane Doe',
        emergency_contact_phone='+20 100 000 0006',
        fitness_goals='Build muscle and improve cardio',
        joined_date=date.today(),
        is_active=True
    )

    db.session.add(customer)
    db.session.commit()

    print(f"✅ Customer profile created: {customer.member_id}")
    print(f"   BMI: {customer.calculate_bmi():.2f} ({customer.get_bmi_category()})")

    return customer

def create_test_subscription_plan():
    """Create a test subscription plan"""
    from app.models.subscription import SubscriptionPlan

    plan = SubscriptionPlan(
        name='Monthly Premium',
        description='Full gym access for 30 days',
        duration_days=30,
        price=500.00,
        access_hours='6AM-10PM',
        includes_trainer=False,
        includes_nutrition=False,
        max_freeze_days=5,
        is_active=True
    )

    db.session.add(plan)
    db.session.commit()
    return plan

def create_test_subscription(customer, plan):
    """Create active subscription for test customer"""
    print("\n📋 Creating test subscription...")

    from datetime import timedelta
    import random

    # Generate unique subscription number
    sub_number = f"SUB-{date.today().year}-{random.randint(1000, 9999)}"

    # Get the receptionist user ID (they create subscriptions)
    receptionist = User.query.filter_by(role='receptionist').first()

    subscription = Subscription(
        customer_id=customer.id,
        branch_id=customer.branch_id,
        plan_id=plan.id,
        subscription_number=sub_number,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=plan.duration_days),
        actual_price=plan.price,
        status='active',
        created_by_id=receptionist.id if receptionist else 1
    )

    db.session.add(subscription)
    db.session.commit()

    print(f"✅ Subscription created: {subscription.subscription_number}")
    return subscription

def create_test_payment(subscription, customer):
    """Create payment record for subscription"""
    print("\n💳 Creating test payment...")

    import random

    # Generate unique payment number
    payment_number = f"PAY-{date.today().year}-{random.randint(1000, 9999)}"

    # Get the receptionist user ID (they process payments)
    receptionist = User.query.filter_by(role='receptionist').first()

    payment = Payment(
        payment_number=payment_number,
        customer_id=customer.id,
        subscription_id=subscription.id,
        branch_id=customer.branch_id,
        amount=subscription.actual_price,
        payment_method='cash',
        status='completed',
        service_type='subscription',
        description=f'Payment for subscription {subscription.subscription_number}',
        reference_number=f"REF-{random.randint(10000, 99999)}",
        processed_by_id=receptionist.id if receptionist else 1
    )

    db.session.add(payment)
    db.session.commit()

    print(f"✅ Payment recorded: {payment.amount} EGP - {payment.payment_number}")
    return payment

    db.session.add(payment)
    db.session.commit()

    print(f"✅ Payment recorded: {payment.amount} EGP")
    return payment

def print_credentials_summary(users):
    """Print a summary of all test credentials"""
    print("\n" + "="*60)
    print("🎉 DATABASE SEEDED SUCCESSFULLY!")
    print("="*60)
    print("\n📝 TEST USER CREDENTIALS:")
    print("-"*60)

    credentials = [
        ("👑 Owner (Central Admin)", "owner", "owner123"),
        ("🏢 Branch Manager", "manager", "manager123"),
        ("🎫 Receptionist (Front Desk)", "receptionist", "receptionist123"),
        ("💰 Accountant", "accountant", "accountant123"),
        ("🏋️ Customer", "customer", "customer123"),
    ]

    for role, username, password in credentials:
        print(f"\n{role}")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   Email:    {username}@gym.com")

    print("\n" + "-"*60)
    print("🌐 Backend Server: http://192.168.1.6:5000")
    print("📱 Flutter App: Connect to above IP address")
    print("="*60)
    print("\n💡 TIP: All users have simple passwords for testing.")
    print("   Remember to change them in production!")
    print("\n")

def main():
    """Main seed function"""
    print("\n" + "="*60)
    print("🌱 STARTING DATABASE SEED PROCESS")
    print("="*60)

    # Create Flask app directly
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        try:
            # Step 1: Reset database
            reset_database()

            # Step 2: Create users
            users = create_test_users()

            # Step 3: Create branches
            branches = create_test_branches(users)

            # Step 4: Create customer profile
            customer = create_test_customer_profile(
                users['customer_user'],
                branches['main_branch']
            )

            # Step 5: Create subscription plan
            plan = create_test_subscription_plan()

            # Step 6: Create subscription
            subscription = create_test_subscription(customer, plan)

            # Step 7: Create payment
            payment = create_test_payment(subscription, customer)

            # Step 8: Print summary
            print_credentials_summary(users)

            print("✅ Seed process completed successfully!")

        except Exception as e:
            print(f"\n❌ Error during seed process: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    main()














