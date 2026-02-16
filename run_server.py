#!/usr/bin/env python3
from app import create_app
from app.database import db

# Create the Flask app
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Create all database tables
        db.create_all()
        print("✅ Database tables created!")
        
        # Create a test user for customer
        from app.models.user import User
        from app.models.customer import Customer
        from app.models.branch import Branch
        from datetime import datetime, date
        
        # Check if test user exists
        existing_user = User.query.filter_by(email='customer@test.com').first()
        
        if existing_user:
            print("✅ Test customer user already exists: customer@test.com")
            print(f"   User ID: {existing_user.id}")
            print(f"   Name: {existing_user.first_name} {existing_user.last_name}")
        else:
            # Create a test branch first if none exists
            test_branch = Branch.query.first()
            if not test_branch:
                test_branch = Branch(
                    name='الفرع الرئيسي',
                    location='الرياض، المملكة العربية السعودية',
                    phone='+966501234567'
                )
                db.session.add(test_branch)
                db.session.commit()
                print("✅ Test branch created")
            
            # Create new test user with customer role
            test_user = User(
                username='customer_test',
                email='customer@test.com',
                first_name='عميل',
                last_name='تجريبي',
                phone='+966501234567',
                role='customer',
                branch_id=test_branch.id,
                is_active=True
            )
            test_user.set_password('password123')
            
            db.session.add(test_user)
            db.session.commit()
            
            # Create customer profile linked to user
            test_customer = Customer(
                user_id=test_user.id,
                branch_id=test_branch.id,
                member_id=f'CUST{test_user.id:04d}',
                date_of_birth=date(1990, 1, 1),
                gender='male',
                height_cm=175.0,
                weight_kg=75.0,
                fitness_goals='تحسين اللياقة البدنية',
                joined_date=date.today()
            )
            
            db.session.add(test_customer)
            db.session.commit()
            
            print("✅ Test customer created successfully!")
            print(f"   Email: customer@test.com")
            print(f"   Password: password123")
            print(f"   User ID: {test_user.id}")
            print(f"   Customer ID: {test_customer.id}")
            print(f"   Name: {test_user.first_name} {test_user.last_name}")
    
    print(f"\n🚀 Starting Flask server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)