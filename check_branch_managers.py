from app import create_app
from app.database import db
from app.models.user import User
from app.models.branch import Branch

app = create_app()
app.app_context().push()

print("\n" + "="*70)
print("           BRANCHES AND THEIR MANAGERS")
print("="*70 + "\n")

branches = Branch.query.all()

for branch in branches:
    print(f"BRANCH: {branch.name}")
    print(f"   ID: {branch.id}")
    print(f"   Code: {branch.code}")
    print(f"   Manager ID in Branch table: {branch.manager_id}")
    
    if branch.manager_id:
        manager = User.query.get(branch.manager_id)
        if manager:
            print(f"   [OK] Manager: {manager.username} ({manager.first_name} {manager.last_name})")
            print(f"   Manager's branch_id: {manager.branch_id}")
        else:
            print(f"   [ERROR] Manager ID {branch.manager_id} not found in users table")
    else:
        print(f"   [NONE] No manager assigned to this branch")
    
    print("-" * 70)

print("\n" + "="*70)
print("           BRANCH MANAGERS AND THEIR ASSIGNMENTS")
print("="*70 + "\n")

managers = User.query.filter_by(role='branch_manager').all()

if not managers:
    print("[ERROR] No branch managers found in the system!")
else:
    for manager in managers:
        print(f"MANAGER: {manager.username}")
        print(f"   ID: {manager.id}")
        print(f"   Name: {manager.first_name} {manager.last_name}")
        print(f"   Email: {manager.email}")
        print(f"   Assigned Branch ID (user.branch_id): {manager.branch_id}")
        
        if manager.branch_id:
            branch = Branch.query.get(manager.branch_id)
            if branch:
                print(f"   [OK] Assigned to branch: {branch.name} ({branch.code})")
                if branch.manager_id == manager.id:
                    print(f"   [OK] Properly linked (branch.manager_id matches)")
                else:
                    print(f"   [WARNING] branch.manager_id is {branch.manager_id}, not {manager.id}!")
            else:
                print(f"   [ERROR] Branch ID {manager.branch_id} not found!")
        else:
            print(f"   [NONE] Not assigned to any branch")
        
        print("-" * 70)

print("\n" + "="*70)
print("           ISSUES FOUND")
print("="*70 + "\n")

issues = []

# Check for managers without branch assignment
unassigned_managers = [m for m in managers if not m.branch_id]
if unassigned_managers:
    issues.append(f"[WARNING] {len(unassigned_managers)} manager(s) not assigned to any branch")

# Check for branches without managers
unmanaged_branches = [b for b in branches if not b.manager_id]
if unmanaged_branches:
    issues.append(f"[WARNING] {len(unmanaged_branches)} branch(es) without a manager")

# Check for mismatched links
for manager in managers:
    if manager.branch_id:
        branch = Branch.query.get(manager.branch_id)
        if branch and branch.manager_id != manager.id:
            issues.append(f"[WARNING] Manager {manager.username} assigned to branch {branch.name}, but branch.manager_id doesn't match")

if issues:
    for issue in issues:
        print(issue)
else:
    print("[OK] No issues found! All branches and managers are properly linked.")

print("\n" + "="*70)
print("           HOW TO ASSIGN A MANAGER TO A BRANCH")
print("="*70 + "\n")

print("Option 1: Using API (Owner only)")
print("  PUT /api/branches/<branch_id>")
print("  Body: { \"manager_id\": <user_id> }")
print()
print("Option 2: Using Python script:")
print("  # Assign manager with ID 2 to branch with ID 1")
print("  branch = Branch.query.get(1)")
print("  manager = User.query.get(2)")
print("  branch.manager_id = manager.id")
print("  manager.branch_id = branch.id")
print("  db.session.commit()")
print()
print("="*70 + "\n")
