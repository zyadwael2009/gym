"""Test JWT fix by writing to file"""
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token, verify_jwt_in_request, get_jwt_identity
from config import Config
from app.database import db
from app.models import user, branch, customer, subscription, payment, attendance, complaint
from app.models.user import User

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
jwt = JWTManager(app)

output = []

with app.app_context():
    output.append("=" * 70)
    output.append("JWT TEST RESULTS")
    output.append("=" * 70)

    # Get user
    user_obj = User.query.filter_by(email='z@gmail.com').first()
    if not user_obj:
        output.append("ERROR: User not found!")
    else:
        output.append(f"User found: ID={user_obj.id} (type: {type(user_obj.id).__name__})")

        # Create token with string
        token = create_access_token(identity=str(user_obj.id))
        output.append(f"Token created with identity=str({user_obj.id})")
        output.append(f"Token: {token[:50]}...")

        # Test verification
        with app.test_request_context('/test', headers={'Authorization': f'Bearer {token}'}):
            try:
                verify_jwt_in_request()
                identity = get_jwt_identity()
                output.append(f"SUCCESS! Token verified!")
                output.append(f"Identity: {identity} (type: {type(identity).__name__})")

                # Query user
                verified_user = User.query.get(int(identity))
                if verified_user:
                    output.append(f"User query successful: {verified_user.username}")
                    output.append("")
                    output.append("=" * 70)
                    output.append("RESULT: JWT FIX WORKS!")
                    output.append("=" * 70)
                else:
                    output.append("ERROR: User not found")
            except Exception as e:
                output.append(f"ERROR: {type(e).__name__}: {e}")
                output.append("")
                output.append("=" * 70)
                output.append("RESULT: JWT FIX FAILED!")
                output.append("=" * 70)

# Write to file
with open('jwt_test_result.txt', 'w') as f:
    f.write('\n'.join(output))

print('\n'.join(output))
