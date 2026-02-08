"""Debug authentication issues"""
import sys
sys.path.insert(0, 'D:/Programming/Flutter/gym/backend')

import app as app_module
from app.database import db
from app.models.user import User
from flask_jwt_extended import create_access_token, decode_token
import json

app = app_module.create_app()

with app.app_context():
    print("=" * 70)
    print("DEBUGGING JWT CONFIGURATION")
    print("=" * 70)

    # Check JWT config
    print("\n1. JWT Configuration:")
    print(f"   JWT_SECRET_KEY: {app.config.get('JWT_SECRET_KEY')[:20]}...")
    print(f"   JWT_ACCESS_TOKEN_EXPIRES: {app.config.get('JWT_ACCESS_TOKEN_EXPIRES')}")

    # Find test user
    print("\n2. Finding test user...")
    user = User.query.filter_by(email='z@gmail.com').first()
    if user:
        print(f"   User found: ID={user.id}, Role={user.role}, Active={user.is_active}")
    else:
        print("   ERROR: User not found!")
        exit(1)

    # Create token
    print("\n3. Creating token...")
    token = create_access_token(identity=user.id)
    print(f"   Token: {token[:50]}...")

    # Try to decode token
    print("\n4. Decoding token...")
    try:
        decoded = decode_token(token)
        print(f"   Decoded successfully!")
        print(f"   Identity: {decoded.get('sub')}")
        print(f"   Type: {decoded.get('type')}")
        print(f"   Expires: {decoded.get('exp')}")
    except Exception as e:
        print(f"   ERROR decoding: {e}")

    # Try to verify with app context
    print("\n5. Testing verify_jwt_in_request...")
    from flask import Flask
    from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

    with app.test_request_context(
        '/test',
        headers={'Authorization': f'Bearer {token}'}
    ):
        try:
            verify_jwt_in_request()
            identity = get_jwt_identity()
            print(f"   Verified successfully!")
            print(f"   Identity from JWT: {identity}")

            # Try to get user
            test_user = User.query.get(identity)
            if test_user:
                print(f"   User query successful: {test_user.username}")
            else:
                print(f"   ERROR: Could not query user with ID {identity}")
        except Exception as e:
            print(f"   ERROR: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 70)
    print("DEBUG COMPLETE")
    print("=" * 70)
