"""Test JWT configuration"""
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

jwt = JWTManager(app)

@app.route('/test/create-token')
def create_token():
    """Create a test token"""
    access_token = create_access_token(identity=1)
    return {'token': access_token}

@app.route('/test/verify-token')
@jwt_required()
def verify_token():
    """Verify a test token"""
    user_id = get_jwt_identity()
    return {'user_id': user_id, 'message': 'Token is valid'}

if __name__ == '__main__':
    print("Testing JWT Configuration...")
    print(f"JWT_SECRET_KEY set: {bool(app.config.get('JWT_SECRET_KEY'))}")
    print(f"JWT_SECRET_KEY: {app.config.get('JWT_SECRET_KEY')[:20]}...")

    with app.app_context():
        # Test token creation
        token = create_access_token(identity=1)
        print(f"\nCreated token: {token[:50]}...")
        print("\nNow start the server and test:")
        print("1. GET http://localhost:5000/test/create-token")
        print("2. GET http://localhost:5000/test/verify-token with Authorization header")

    app.run(host='0.0.0.0', port=5001, debug=True)
