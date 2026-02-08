"""Authentication API routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from datetime import datetime
from app.database import db
from app.models.user import User
from app.auth import validate_json_request

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
@validate_json_request('username', 'password')
def login():
    """User login endpoint"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # Find user by username or email
    user = User.query.filter(
        (User.username == username) | (User.email == username)
    ).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is inactive'}), 401
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Create tokens - JWT requires identity to be a string
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict(),
        'message': 'Login successful'
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))  # Convert string back to int

    if not user or not user.is_active:
        return jsonify({'error': 'User not found or inactive'}), 401
    
    access_token = create_access_token(identity=str(current_user_id))

    return jsonify({
        'access_token': access_token,
        'message': 'Token refreshed successfully'
    }), 200

@auth_bp.route('/register', methods=['POST'])
@validate_json_request('username', 'email', 'password', 'first_name', 'last_name', 'role')
def register():
    """User registration (admin only in production)"""
    data = request.get_json()
    
    # Check if username or email already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Validate role
    valid_roles = ['owner', 'branch_manager', 'receptionist', 'accountant', 'customer']
    if data['role'] not in valid_roles:
        return jsonify({'error': 'Invalid role', 'valid_roles': valid_roles}), 400
    
    # Create new user
    user = User(
        username=data['username'],
        email=data['email'],
        role=data['role'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        phone=data.get('phone'),
        branch_id=data.get('branch_id')
    )
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
@validate_json_request('current_password', 'new_password')
def change_password():
    """Change user password"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not user.check_password(current_password):
        return jsonify({'error': 'Current password is incorrect'}), 400
    
    if len(new_password) < 6:
        return jsonify({'error': 'New password must be at least 6 characters long'}), 400
    
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'message': 'Password changed successfully'}), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    profile_data = user.to_dict()
    
    # Add branch information if user has a branch
    if user.branch:
        profile_data['branch'] = user.branch.to_dict()
    
    # Add customer profile if user is a customer
    if user.role == 'customer' and user.customer_profile:
        profile_data['customer_profile'] = user.customer_profile.to_dict(include_health=True)
    
    return jsonify(profile_data), 200

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Update allowed fields
    updatable_fields = ['first_name', 'last_name', 'phone', 'email']
    
    for field in updatable_fields:
        if field in data and data[field] is not None:
            # Check email uniqueness
            if field == 'email' and data[field] != user.email:
                if User.query.filter_by(email=data[field]).first():
                    return jsonify({'error': 'Email already exists'}), 400
            
            setattr(user, field, data[field])
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Update failed', 'details': str(e)}), 500

@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    """List users (admin functionality)"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if current_user.role not in ['owner', 'branch_manager']:
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    # Filter by branch for branch managers
    query = User.query
    if current_user.role == 'branch_manager':
        query = query.filter_by(branch_id=current_user.branch_id)
    
    # Apply filters
    role = request.args.get('role')
    if role:
        query = query.filter_by(role=role)
    
    is_active = request.args.get('is_active')
    if is_active is not None:
        query = query.filter_by(is_active=is_active.lower() == 'true')
    
    users = query.all()
    
    return jsonify({
        'users': [user.to_dict() for user in users],
        'total': len(users)
    }), 200
