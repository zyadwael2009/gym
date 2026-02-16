#!/usr/bin/env python3
"""
Create test customer for the gym customer app
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from app import create_app
from app.database import db
from app.models.customer import Customer

def create_test_customer():
    """Create a test customer for the app"""
    app = create_app()
    
    with app.app_context():
        # Check if test customer already exists
        existing_customer = Customer.query.filter_by(email='customer@test.com').first()
        
        if existing_customer:
            print("Test customer already exists!")
            print(f"Email: {existing_customer.email}")
            print(f"Phone: {existing_customer.phone} (use as password)")
            print(f"Name: {existing_customer.name}")
            return existing_customer
        
        # Create test customer
        customer = Customer(
            name='أحمد محمد العميل',
            email='customer@test.com',
            phone='password123',  # Using phone as password for simplicity
            address='الرياض، المملكة العربية السعودية',
            emergency_contact='0501234567',
            notes='عميل تجريبي للاختبار',
            subscription_status='active',
            subscription_type='monthly',
            subscription_start_date=datetime.now(),
            subscription_end_date=datetime.now() + timedelta(days=30),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            branch_id=1  # Default branch
        )
        
        try:
            db.session.add(customer)
            db.session.commit()
            
            print("✅ Test customer created successfully!")
            print(f"📧 Email: {customer.email}")
            print(f"🔑 Password: {customer.phone}")
            print(f"👤 Name: {customer.name}")
            print(f"🏢 Branch ID: {customer.branch_id}")
            print(f"📱 Login URL: http://localhost:8081")
            
            return customer
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating test customer: {e}")
            return None

if __name__ == '__main__':
    create_test_customer()