from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta
import jwt

app = Flask(__name__)
CORS(app)

# Simple configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Simple in-memory data store for demo
users = [
    {'id': 1, 'username': 'admin', 'password': 'admin', 'role': 'owner', 'email': 'admin@gym.com'},
    {'id': 2, 'username': 'manager', 'password': 'manager', 'role': 'branch_manager', 'email': 'manager@gym.com'},
    {'id': 3, 'username': 'receptionist', 'password': 'receptionist', 'role': 'receptionist', 'email': 'receptionist@gym.com'},
]

customers = [
    {'id': 1, 'name': 'John Doe', 'email': 'john@example.com', 'phone': '+1234567890', 'branch_id': 1, 'is_active': True},
    {'id': 2, 'name': 'Jane Smith', 'email': 'jane@example.com', 'phone': '+1234567891', 'branch_id': 1, 'is_active': True},
]

branches = [
    {'id': 1, 'name': 'Downtown Gym', 'address': '123 Main St', 'phone': '+1234567890', 'email': 'downtown@gym.com', 'is_active': True},
]

def generate_token(user):
    payload = {
        'user_id': user['id'],
        'username': user['username'],
        'role': user['role'],
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = next((u for u in users if u['username'] == username and u['password'] == password), None)

        if user:
            token = generate_token(user)
            user_data = {k: v for k, v in user.items() if k != 'password'}
            return jsonify({
                'success': True,
                'data': {
                    'token': token,
                    'user': user_data
                },
                'message': 'Login successful'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid credentials'
            }), 401
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    return jsonify({
        'success': True,
        'message': 'Logout successful'
    })

@app.route('/api/customers', methods=['GET'])
def get_customers():
    return jsonify({
        'success': True,
        'data': customers
    })

@app.route('/api/branches', methods=['GET'])
def get_branches():
    return jsonify({
        'success': True,
        'data': branches
    })

@app.route('/api/dashboard/overview', methods=['GET'])
def get_dashboard_overview():
    return jsonify({
        'success': True,
        'data': {
            'total_customers': len(customers),
            'active_subscriptions': 180,
            'todays_attendance': 45,
            'monthly_revenue': 12500
        }
    })

@app.route('/')
def index():
    return jsonify({
        'message': 'Gym Management API',
        'status': 'running'
    })

if __name__ == '__main__':
    print("Starting Gym Management API...")
    print("API will be available at: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
