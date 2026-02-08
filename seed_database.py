import importlib.util
from datetime import date, datetime, timedelta

# Import the main app
spec = importlib.util.spec_from_file_location('main_app', 'app.py')
main_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_app)

# Import database and models
from app.database import db
from app.models.user import User
from app.models.branch import Branch
from app.models.customer import Customer
from app.models.subscription import SubscriptionPlan

app = main_app.create_app()

with app.app_context():
    # Create all tables
    db.create_all()
    
    # Check if data already exists
    if Branch.query.first():
        print("Data already exists")
        exit()
    
    print("Seeding database...")
    
    # Create branches
    branches_data = [
        {'name': 'Downtown Gym', 'code': 'DT', 'phone': '+1-555-0101'},
        {'name': 'Uptown Fitness', 'code': 'UT', 'phone': '+1-555-0102'},
        {'name': 'Westside Wellness', 'code': 'WS', 'phone': '+1-555-0103'}
    ]
    
    branches = []
    for branch_data in branches_data:
        branch = Branch(
            name=branch_data['name'],
            code=branch_data['code'],
            address_line1="123 Main St",
            city="Sample City",
            state="Sample State",
            pincode="12345",
            phone=branch_data['phone'],
            email=f"{branch_data['code'].lower()}@gym.com"
        )
        db.session.add(branch)
        branches.append(branch)
    
    db.session.flush()
    
    # Create users
    users_data = [
        {'username': 'owner', 'email': 'owner@gym.com', 'password': 'owner123', 
         'role': 'owner', 'first_name': 'System', 'last_name': 'Owner'},
        {'username': 'manager.downtown', 'email': 'manager.downtown@gym.com', 'password': 'manager123', 
         'role': 'branch_manager', 'first_name': 'John', 'last_name': 'Manager', 'branch_id': branches[0].id},
        {'username': 'manager.uptown', 'email': 'manager.uptown@gym.com', 'password': 'manager123', 
         'role': 'branch_manager', 'first_name': 'Jane', 'last_name': 'Manager', 'branch_id': branches[1].id},
        {'username': 'receptionist', 'email': 'receptionist@gym.com', 'password': 'receptionist123', 
         'role': 'receptionist', 'first_name': 'Alice', 'last_name': 'Receptionist', 'branch_id': branches[0].id},
        {'username': 'accountant', 'email': 'accountant@gym.com', 'password': 'accountant123', 
         'role': 'accountant', 'first_name': 'Bob', 'last_name': 'Accountant', 'branch_id': branches[0].id},
    ]
    
    for user_data in users_data:
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            role=user_data['role'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            branch_id=user_data.get('branch_id'),
            phone="+1-555-0100"
        )
        user.set_password(user_data['password'])
        db.session.add(user)
    
    # Create subscription plans
    plans_data = [
        {'name': 'Basic Monthly', 'duration_days': 30, 'price': 49.99},
        {'name': 'Premium Monthly', 'duration_days': 30, 'price': 99.99},
        {'name': 'VIP Monthly', 'duration_days': 30, 'price': 149.99},
        {'name': 'Annual Premium', 'duration_days': 365, 'price': 999.99},
    ]
    
    for plan_data in plans_data:
        plan = SubscriptionPlan(
            name=plan_data['name'],
            duration_days=plan_data['duration_days'],
            price=plan_data['price'],
            description=f"{plan_data['name']} membership plan",
            max_freeze_days=30,
            is_active=True
        )
        db.session.add(plan)
    
    db.session.commit()
    
    print("Database seeded successfully!")
    print("Default login credentials:")
    print("- Owner: owner@gym.com / owner123")
    print("- Manager: manager.downtown@gym.com / manager123")  
    print("- Receptionist: receptionist@gym.com / receptionist123")
    print("- Accountant: accountant@gym.com / accountant123")

print("Seeding complete!")