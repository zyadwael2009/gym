from app import create_app
from app.database import db
from app.models.user import User
from app.models.branch import Branch

app = create_app()
app.app_context().push()

print("Assigning manager to branch 1...")

# Get branch 1
branch = Branch.query.get(1)
if not branch:
    print("ERROR: Branch 1 not found!")
    exit(1)

# Get manager user (ID 2)
manager = User.query.get(2)
if not manager:
    print("ERROR: Manager user (ID 2) not found!")
    exit(1)

print(f"Branch: {branch.name} (ID: {branch.id})")
print(f"Manager: {manager.username} - {manager.first_name} {manager.last_name}")

# Assign both ways
branch.manager_id = manager.id
manager.branch_id = branch.id

db.session.commit()

print("\n✅ Manager assigned successfully!")
print(f"   Branch '{branch.name}' now has manager '{manager.username}'")
print(f"   Manager '{manager.username}' is assigned to branch '{branch.name}'")
