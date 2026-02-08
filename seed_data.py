"""Database seeding script with sample data"""
from flask import Flask, current_app
from flask.cli import with_appcontext
from datetime import date, datetime, timedelta
import click
from app.database import db
from app.models.user import User
from app.models.branch import Branch
from app.models.customer import Customer, HealthReport
from app.models.subscription import SubscriptionPlan, Subscription
from app.models.payment import Payment
from app.models.attendance import Attendance
from app.models.complaint import Complaint

@click.command()
@with_appcontext
def seed_db():
    """Seed database with sample data"""
    print("Seeding database...")
    
    # Clear existing data
    db.session.query(Attendance).delete()
    db.session.query(Payment).delete()
    db.session.query(Subscription).delete()
    db.session.query(SubscriptionPlan).delete()
    db.session.query(HealthReport).delete()
    db.session.query(Customer).delete()
    db.session.query(Complaint).delete()
    db.session.query(User).delete()
    db.session.query(Branch).delete()
    
    # Create Branches
    print("Creating branches...")
    branches = [
        Branch(
            name="Downtown Fitness Center",
            code="DT01",
            address_line1="123 Main Street",
            city="Mumbai",
            state="Maharashtra",
            pincode="400001",
            phone="+91-98765-43210",
            email="downtown@gymmanager.com",
            monthly_target=100000
        ),
        Branch(
            name="Suburban Health Club",
            code="SB02",
            address_line1="456 Park Avenue",
            city="Pune",
            state="Maharashtra",
            pincode="411001",
            phone="+91-98765-43211",
            email="suburban@gymmanager.com",
            monthly_target=75000
        ),
        Branch(
            name="Elite Fitness Hub",
            code="EL03",
            address_line1="789 Business District",
            city="Bangalore",
            state="Karnataka",
            pincode="560001",
            phone="+91-98765-43212",
            email="elite@gymmanager.com",
            monthly_target=120000
        )
    ]
    
    for branch in branches:
        db.session.add(branch)
    
    db.session.commit()
    print(f"Created {len(branches)} branches")
    
    # Create Users
    print("Creating users...")
    users = [
        # Owner
        User(
            username="admin",
            email="admin@gymmanager.com",
            role="owner",
            first_name="John",
            last_name="Smith",
            phone="+91-99999-00001"
        ),
        # Branch Managers
        User(
            username="manager1",
            email="manager1@gymmanager.com",
            role="branch_manager",
            first_name="Sarah",
            last_name="Johnson",
            phone="+91-99999-00002",
            branch_id=1
        ),
        User(
            username="manager2",
            email="manager2@gymmanager.com",
            role="branch_manager",
            first_name="Mike",
            last_name="Wilson",
            phone="+91-99999-00003",
            branch_id=2
        ),
        # Receptionists
        User(
            username="reception1",
            email="reception1@gymmanager.com",
            role="receptionist",
            first_name="Emily",
            last_name="Davis",
            phone="+91-99999-00004",
            branch_id=1
        ),
        User(
            username="reception2",
            email="reception2@gymmanager.com",
            role="receptionist",
            first_name="James",
            last_name="Brown",
            phone="+91-99999-00005",
            branch_id=2
        ),
        # Accountants
        User(
            username="accountant1",
            email="accountant1@gymmanager.com",
            role="accountant",
            first_name="Lisa",
            last_name="Garcia",
            phone="+91-99999-00006",
            branch_id=1
        )
    ]
    
    # Set passwords for all users
    for user in users:
        user.set_password("password123")
        db.session.add(user)
    
    db.session.commit()
    print(f"Created {len(users)} staff users")
    
    # Update branch managers
    branches[0].manager_id = 2  # Sarah Johnson
    branches[1].manager_id = 3  # Mike Wilson
    
    # Create Subscription Plans
    print("Creating subscription plans...")
    plans = [
        SubscriptionPlan(
            name="Basic Monthly",
            description="Basic gym access for 1 month",
            duration_days=30,
            price=1500,
            access_hours="6AM-10PM",
            includes_trainer=False,
            includes_nutrition=False,
            max_freeze_days=5
        ),
        SubscriptionPlan(
            name="Premium Monthly",
            description="Premium gym access with trainer for 1 month",
            duration_days=30,
            price=2500,
            access_hours="24x7",
            includes_trainer=True,
            includes_nutrition=False,
            max_freeze_days=7
        ),
        SubscriptionPlan(
            name="Elite Quarterly",
            description="Elite access with trainer and nutrition for 3 months",
            duration_days=90,
            price=6000,
            access_hours="24x7",
            includes_trainer=True,
            includes_nutrition=True,
            max_freeze_days=15
        ),
        SubscriptionPlan(
            name="Annual Gold",
            description="Annual membership with all benefits",
            duration_days=365,
            price=18000,
            access_hours="24x7",
            includes_trainer=True,
            includes_nutrition=True,
            max_freeze_days=30
        )
    ]
    
    for plan in plans:
        db.session.add(plan)
    
    db.session.commit()
    print(f"Created {len(plans)} subscription plans")
    
    # Create Customer Users and Customers
    print("Creating customers...")
    customers_data = [
        {
            'username': 'rajesh.kumar',
            'email': 'rajesh.kumar@gmail.com',
            'first_name': 'Rajesh',
            'last_name': 'Kumar',
            'phone': '+91-98765-11111',
            'branch_id': 1,
            'dob': date(1990, 5, 15),
            'gender': 'male',
            'height': 175,
            'weight': 70
        },
        {
            'username': 'priya.sharma',
            'email': 'priya.sharma@gmail.com',
            'first_name': 'Priya',
            'last_name': 'Sharma',
            'phone': '+91-98765-22222',
            'branch_id': 1,
            'dob': date(1985, 8, 20),
            'gender': 'female',
            'height': 160,
            'weight': 55
        },
        {
            'username': 'amit.patel',
            'email': 'amit.patel@gmail.com',
            'first_name': 'Amit',
            'last_name': 'Patel',
            'phone': '+91-98765-33333',
            'branch_id': 2,
            'dob': date(1988, 12, 10),
            'gender': 'male',
            'height': 180,
            'weight': 85
        },
        {
            'username': 'sneha.reddy',
            'email': 'sneha.reddy@gmail.com',
            'first_name': 'Sneha',
            'last_name': 'Reddy',
            'phone': '+91-98765-44444',
            'branch_id': 2,
            'dob': date(1992, 3, 5),
            'gender': 'female',
            'height': 165,
            'weight': 58
        }
    ]
    
    customers = []
    for i, customer_data in enumerate(customers_data):
        # Create user account
        user = User(
            username=customer_data['username'],
            email=customer_data['email'],
            role='customer',
            first_name=customer_data['first_name'],
            last_name=customer_data['last_name'],
            phone=customer_data['phone'],
            branch_id=customer_data['branch_id']
        )
        user.set_password('customer123')
        db.session.add(user)
        db.session.flush()
        
        # Create customer profile
        branch_code = 'DT01' if customer_data['branch_id'] == 1 else 'SB02'
        member_id = f"{branch_code}{date.today().strftime('%y%m%d')}{str(i+1).zfill(4)}"
        
        customer = Customer(
            user_id=user.id,
            branch_id=customer_data['branch_id'],
            member_id=member_id,
            date_of_birth=customer_data['dob'],
            gender=customer_data['gender'],
            height_cm=customer_data['height'],
            weight_kg=customer_data['weight'],
            emergency_contact_name=f"Emergency Contact {i+1}",
            emergency_contact_phone=f"+91-99999-{str(i+1).zfill(5)}",
            fitness_goals="Weight loss and muscle building"
        )
        db.session.add(customer)
        customers.append(customer)
    
    db.session.commit()
    print(f"Created {len(customers)} customers")
    
    # Create Subscriptions
    print("Creating subscriptions...")
    subscriptions = []
    today = date.today()
    
    for i, customer in enumerate(customers):
        # Create subscription
        plan_id = (i % 3) + 1  # Distribute plans
        start_date = today - timedelta(days=30 - (i * 5))  # Stagger start dates
        
        subscription = Subscription(
            customer_id=customer.id,
            plan_id=plan_id,
            branch_id=customer.branch_id,
            subscription_number=f"SUB{customer.branch.code}{start_date.strftime('%y%m%d')}{str(i+1).zfill(6)}",
            start_date=start_date,
            end_date=start_date + timedelta(days=30),
            actual_price=plans[plan_id-1].price,
            status='active',
            created_by_id=4  # Reception1
        )
        db.session.add(subscription)
        subscriptions.append(subscription)
    
    db.session.commit()
    print(f"Created {len(subscriptions)} subscriptions")
    
    # Create Payments
    print("Creating payments...")
    for i, subscription in enumerate(subscriptions):
        payment = Payment(
            payment_number=f"PAY{date.today().strftime('%y%m%d')}{str(i+1).zfill(8)}",
            amount=subscription.actual_price,
            payment_method=['cash', 'card', 'upi'][i % 3],
            status='completed',
            customer_id=subscription.customer_id,
            subscription_id=subscription.id,
            branch_id=subscription.branch_id,
            service_type='subscription',
            description=f"Payment for {subscription.plan.name}",
            processed_by_id=4  # Reception1
        )
        db.session.add(payment)
    
    db.session.commit()
    print(f"Created {len(subscriptions)} payments")
    
    # Create Attendance Records
    print("Creating attendance records...")
    attendance_count = 0
    for customer in customers:
        # Create attendance for last 10 days
        for days_back in range(10):
            if days_back % 3 == 0:  # Not every day
                continue
            
            entry_date = today - timedelta(days=days_back)
            attendance = Attendance(
                customer_id=customer.id,
                branch_id=customer.branch_id,
                entry_date=entry_date,
                entry_method='manual',
                access_granted=True,
                processed_by_id=4
            )
            db.session.add(attendance)
            attendance_count += 1
    
    db.session.commit()
    print(f"Created {attendance_count} attendance records")
    
    # Create Sample Complaints
    print("Creating complaints...")
    complaints = [
        Complaint(
            complaint_number=f"CMP{date.today().strftime('%y%m%d')}000001",
            title="Equipment malfunction",
            description="The treadmill in section A is making strange noises and stops suddenly.",
            category="equipment",
            priority="medium",
            customer_id=customers[0].id,
            branch_id=customers[0].branch_id,
            status="open"
        ),
        Complaint(
            complaint_number=f"CMP{date.today().strftime('%y%m%d')}000002",
            title="Cleanliness issue in locker room",
            description="The men's locker room was not properly cleaned yesterday evening.",
            category="cleanliness",
            priority="low",
            customer_id=customers[2].id,
            branch_id=customers[2].branch_id,
            status="in_progress",
            assigned_to_id=3  # Manager2
        )
    ]
    
    for complaint in complaints:
        db.session.add(complaint)
    
    db.session.commit()
    print(f"Created {len(complaints)} complaints")
    
    print("\
✅ Database seeding completed successfully!")
    print("\
📋 Summary:")
    print(f"• {len(branches)} Branches")
    print(f"• {len(users)} Staff Users")
    print(f"• {len(customers)} Customers")
    print(f"• {len(plans)} Subscription Plans")
    print(f"• {len(subscriptions)} Subscriptions")
    print(f"• {len(subscriptions)} Payments")
    print(f"• {attendance_count} Attendance Records")
    print(f"• {len(complaints)} Complaints")
    
    print("\
🔑 Default Login Credentials:")
    print("Owner: admin / password123")
    print("Manager 1: manager1 / password123 (Branch 1)")
    print("Manager 2: manager2 / password123 (Branch 2)")
    print("Reception 1: reception1 / password123 (Branch 1)")
    print("Reception 2: reception2 / password123 (Branch 2)")
    print("Accountant 1: accountant1 / password123 (Branch 1)")
    print("\
Customers: All customers have password 'customer123'")
    print("Customer usernames: rajesh.kumar, priya.sharma, amit.patel, sneha.reddy")

def register_seed_command(app):
    """Register seed command with Flask app"""
    app.cli.add_command(seed_db)
