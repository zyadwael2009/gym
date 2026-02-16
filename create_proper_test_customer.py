#!/usr/bin/env python3
"""
Create test customer with proper User account for the new system
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, date
from app import create_app
from app.database import db
from app.models.user import User
from app.models.customer import Customer
from app.models.branch import Branch

def create_proper_test_customer():
    """Create a test customer with User account"""
    app = create_app()
    
    with app.app_context():
        print("=" * 70)
        print("CREATING TEST CUSTOMER WITH USER ACCOUNT")
        print("=" * 70)
        
        # Get first branch
        branch = Branch.query.first()
        if not branch:
            print("❌ No branches found! Please create branches first.")
            return
        
        print(f"\n📍 Using Branch: {branch.name} (ID: {branch.id})")
        
        # Check if test customer user already exists
        existing_user = User.query.filter_by(email='customer@test.com').first()
        
        if existing_user:
            print("\n⚠️  Test customer user already exists!")
            print(f"📧 Email: {existing_user.email}")
            print(f"👤 Name: {existing_user.first_name} {existing_user.last_name}")
            print(f"🔑 Password: test123")
            
            # Check if customer profile exists
            customer = Customer.query.filter_by(user_id=existing_user.id).first()
            if customer:
                print(f"🆔 Member ID: {customer.member_id}")
                print(f"📱 Phone: {customer.user.phone}")
            return existing_user, customer
        
        # Generate member ID
        member_id = f"{branch.code}{date.today().strftime('%y%m%d')}0001"
        
        # Create user account
        try:
            user = User(
                username='testcustomer',
                email='customer@test.com',
                role='customer',
                first_name='أحمد',
                last_name='محمد',
                phone='+966501234567',
                branch_id=branch.id,
                is_active=True,
                created_at=datetime.utcnow()
            )
            user.set_password('test123')
            
            db.session.add(user)
            db.session.flush()  # Get user ID
            
            # Create customer profile
            customer = Customer(
                user_id=user.id,
                branch_id=branch.id,
                member_id=member_id,
                date_of_birth=date(1990, 1, 1),
                gender='male',
                emergency_contact_name='فاطمة محمد',
                emergency_contact_phone='+966509876543',
                height_cm=175.0,
                weight_kg=75.0,
                fitness_goals='بناء العضلات وتحسين اللياقة البدنية',
                medical_conditions='لا يوجد'
            )
            
            db.session.add(customer)
            db.session.commit()
            
            print("\n✅ Test customer created successfully!")
            print(f"\n📧 Email: {user.email}")
            print(f"🔑 Password: test123")
            print(f"👤 Name: {user.first_name} {user.last_name}")
            print(f"🆔 Member ID: {customer.member_id}")
            print(f"📱 Phone: {user.phone}")
            print(f"🏢 Branch: {branch.name}")
            print(f"\n💡 Use these credentials in the customer app:")
            print(f"   Email: customer@test.com")
            print(f"   Password: test123")
            
            return user, customer
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating test customer: {e}")
            import traceback
            traceback.print_exc()
            return None, None


if __name__ == '__main__':
    create_proper_test_customer()
