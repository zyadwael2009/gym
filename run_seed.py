"""Script to run database seeding"""
from app import create_app
from app.database import db

app = create_app()

with app.app_context():
    # Create all tables
    db.create_all()
    print("Database tables created.")

    # Import and run seeding
    from seed_data import seed_db

    # Run the seed function
    seed_db.callback()
    print("Database seeding complete!")
