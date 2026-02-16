"""Check if customer exists and test password"""
from app.database import db
from app.models.user import User
from app.models.customer import Customer
from app import create_app

app = create_app()
with app.app_context():
    # Find customer by email
    customer_user = User.query.filter_by(email='customer@test.com').first()
    
    if customer_user:
        print(f"✅ Customer found:")
        print(f"   Username: {customer_user.username}")
        print(f"   Email: {customer_user.email}")
        print(f"   Role: {customer_user.role}")
        print(f"   Active: {customer_user.is_active}")
        
        # Test password
        passwords_to_test = ['test123', 'password123', 'customer123']
        for pwd in passwords_to_test:
            if customer_user.check_password(pwd):
                print(f"\n✅ Correct password: {pwd}")
                break
        else:
            print(f"\n❌ None of the test passwords work")
            print(f"   Tried: {passwords_to_test}")
        
        # Check customer profile
        customer_profile = Customer.query.filter_by(user_id=customer_user.id).first()
        if customer_profile:
            print(f"\n✅ Customer profile exists:")
            print(f"   Customer ID: {customer_profile.id}")
            print(f"   Member ID: {customer_profile.member_id}")
            print(f"   Branch ID: {customer_profile.branch_id}")
        else:
            print(f"\n❌ No customer profile found")
    else:
        print(f"❌ No customer found with email: customer@test.com")
        
        # List all customers
        all_customers = User.query.filter_by(role='customer').all()
        print(f"\nTotal customers in database: {len(all_customers)}")
        for c in all_customers[:5]:
            print(f"  - {c.email} ({c.username})")
