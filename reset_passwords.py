"""Reset and seed database with proper users"""
import sys
import os

# Add backend directory to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Import the app factory using importlib to avoid conflicts
import importlib.util

# Load app.py as a module
app_py_path = os.path.join(backend_dir, "app.py")
spec = importlib.util.spec_from_file_location("app_main", app_py_path)
app_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_main)

# Get the Flask app
app = app_main.create_app()

# Now we can import models within the app context
with app.app_context():
    from app.database import db
    from app.models.user import User
    from app.models.branch import Branch

    # Create all tables
    db.create_all()

    # Update all existing users passwords
    users = User.query.all()
    for user in users:
        user.set_password('password123')
    db.session.commit()

    print("=== LOGIN CREDENTIALS ===")
    for user in users:
        print(f"Username: {user.username}, Role: {user.role}, Password: password123")

    with open(os.path.join(backend_dir, 'login_info.txt'), 'w') as f:
        f.write("=== LOGIN CREDENTIALS ===\n")
        for user in users:
            f.write(f"Username: {user.username}, Role: {user.role}, Password: password123\n")
    print("\nSaved to login_info.txt")
