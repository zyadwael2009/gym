"""Quick script to check branches in database"""
from app import create_app
from app.database import db
from app.models.branch import Branch
from app.models.user import User

# Need to import app.py's create_app
import importlib.util
spec = importlib.util.spec_from_file_location("app_main", "app.py")
app_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_main)

app = app_main.create_app()

with app.app_context():
    branches = Branch.query.all()
    print("\n📊 Branches in database:")
    print("-" * 60)
    for b in branches:
        print(f"  ID: {b.id}")
        print(f"  Name: {b.name}")
        print(f"  Code: {b.code}")
        print(f"  Active: {b.is_active}")
        print("-" * 60)

    print(f"\nTotal branches: {len(branches)}")

