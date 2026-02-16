from app import create_app
from app.database import db
from app.models.user import User
from app.models.branch import Branch

app = create_app()
app.app_context().push()

print("\n" + "="*70)
print("           CREATING MANAGER FOR BRANCH 2")
print("="*70 + "\n")

# Check if Branch 2 exists
branch2 = Branch.query.get(2)
if not branch2:
    print("[ERROR] Branch 2 not found!")
    print("Creating branch 2...")
    branch2 = Branch(
        name="North Branch - Nasr City",
        code="NORTH01",
        address_line1="123 Nasr City",
        city="Cairo",
        monthly_target=50000,
        is_active=True
    )
    db.session.add(branch2)
    db.session.commit()
    print(f"[OK] Created branch: {branch2.name}")

print(f"Branch: {branch2.name} (ID: {branch2.id})")

# Check if there's an existing branch manager for branch 2
existing_manager = User.query.filter_by(role='branch_manager', branch_id=2).first()

if existing_manager:
    print(f"\n[INFO] Manager already assigned to branch 2:")
    print(f"  Username: {existing_manager.username}")
    print(f"  Name: {existing_manager.first_name} {existing_manager.last_name}")
else:
    # Create new branch manager for branch 2
    print("\n[INFO] Creating new branch manager for branch 2...")
    
    manager2 = User(
        username="manager2",
        email="manager2@gym.com",
        role="branch_manager",
        first_name="Branch",
        last_name="Manager 2",
        phone="+1234567891",
        is_active=True,
        branch_id=2
    )
    manager2.set_password("password123")
    
    db.session.add(manager2)
    db.session.flush()  # Get the ID
    
    # Assign manager to branch
    branch2.manager_id = manager2.id
    
    db.session.commit()
    
    print(f"\n[OK] Branch manager created successfully!")
    print(f"  Username: manager2")
    print(f"  Password: password123")
    print(f"  Email: manager2@gym.com")
    print(f"  Assigned to: {branch2.name}")

print("\n" + "="*70)
print("           VERIFICATION")
print("="*70 + "\n")

# Verify all branch-manager assignments
branches = Branch.query.all()
for branch in branches:
    print(f"Branch {branch.id}: {branch.name}")
    if branch.manager_id:
        manager = User.query.get(branch.manager_id)
        print(f"  Manager: {manager.username} ({manager.first_name} {manager.last_name})")
    else:
        print(f"  Manager: [NONE]")

print("\n" + "="*70)
print("           LOGIN CREDENTIALS FOR BRANCH MANAGERS")
print("="*70 + "\n")

managers = User.query.filter_by(role='branch_manager').all()
for manager in managers:
    branch = Branch.query.get(manager.branch_id) if manager.branch_id else None
    print(f"Username: {manager.username}")
    print(f"Password: password123")
    print(f"Branch: {branch.name if branch else 'Not assigned'}")
    print("-" * 70)

print("\n")
