"""Simple JWT debug - direct approach"""
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token, verify_jwt_in_request, get_jwt_identity
from flask_cors import CORS
from config import Config
from app.database import db

# Create app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)
CORS(app)

# Import ALL models to register them with SQLAlchemy
from app.models import user, branch, customer, subscription, payment, attendance, complaint
from app.models.user import User

with app.app_context():
    print("=" * 70)
    print("JWT CONFIGURATION DEBUG")
    print("=" * 70)

    # Check config
    print(f"\n1. Configuration:")
    print(f"   JWT_SECRET_KEY: {app.config['JWT_SECRET_KEY'][:20]}...")
    print(f"   SECRET_KEY: {app.config['SECRET_KEY'][:20]}...")
    print(f"   JWT_ACCESS_TOKEN_EXPIRES: {app.config['JWT_ACCESS_TOKEN_EXPIRES']}")

    # Get user
    print(f"\n2. Finding user...")
    user = User.query.filter_by(email='z@gmail.com').first()
    if not user:
        print("   ERROR: User not found!")
        exit(1)
    print(f"   Found: ID={user.id}, Username={user.username}, Role={user.role}")

    # Create token
    print(f"\n3. Creating token...")
    token = create_access_token(identity=str(user.id))  # JWT requires string identity
    print(f"   Token created: {token[:60]}...")

    # Test verification in request context
    print(f"\n4. Testing token verification...")
    with app.test_request_context(
        '/api/dashboard/owner',
        headers={'Authorization': f'Bearer {token}'}
    ):
        try:
            verify_jwt_in_request()
            identity = get_jwt_identity()
            print(f"   SUCCESS! Identity from token: {identity} (type: {type(identity).__name__})")

            # Try to query user - convert string back to int
            verified_user = User.query.get(int(identity))
            if verified_user:
                print(f"   User query successful: {verified_user.username}")
            else:
                print(f"   ERROR: User not found in DB with ID {identity}")
        except Exception as e:
            print(f"   ERROR: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 70)
    print("If the above test SUCCEEDED, then the issue is in the decorator logic")
    print("If the above test FAILED, then the issue is in JWT configuration")
    print("=" * 70)
