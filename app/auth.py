"""Authentication and authorization decorators"""
from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from app.models.user import User
from app.database import db

def jwt_required_custom(f):
    """Custom JWT required decorator with user loading"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Verify JWT token
            verify_jwt_in_request()
            identity = get_jwt_identity()

            # Handle both formats: "customer_123" and "123"
            if identity.startswith('customer_'):
                # Customer format: "customer_123"
                customer_id = int(identity.split('_')[1])
                # Get the user via customer profile
                from app.models.customer import Customer
                customer = db.session.get(Customer, customer_id)
                if not customer:
                    print(f"JWT Error: Customer ID {customer_id} not found in database")
                    return jsonify({'error': 'Customer not found'}), 401
                current_user = customer.user
            else:
                # Staff format: "123"
                user_id = int(identity)
                current_user = db.session.get(User, user_id)

            if not current_user:
                print(f"JWT Error: User with identity {identity} not found in database")
                return jsonify({'error': 'User not found'}), 401

            if not current_user.is_active:
                print(f"JWT Error: User ID {current_user.id} is inactive")
                return jsonify({'error': 'User account is inactive'}), 401

            # Add current_user to kwargs
            kwargs['current_user'] = current_user
            return f(*args, **kwargs)
        except Exception as e:
            # Log the actual error for debugging
            print(f"JWT Error: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': 'Invalid or expired token'}), 401

    return decorated_function

def require_role(*allowed_roles):
    """Decorator to check if user has required role"""
    def decorator(f):
        @wraps(f)
        @jwt_required_custom
        def decorated_function(*args, **kwargs):
            current_user = kwargs.get('current_user')
            
            if current_user.role not in allowed_roles:
                return jsonify({
                    'error': 'Insufficient permissions',
                    'required_roles': list(allowed_roles),
                    'user_role': current_user.role
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_branch_access(branch_id_param='branch_id'):
    """Decorator to check if user has access to specific branch"""
    def decorator(f):
        @wraps(f)
        @jwt_required_custom
        def decorated_function(*args, **kwargs):
            current_user = kwargs.get('current_user')
            
            # Get branch_id from different sources
            branch_id = None
            
            # Try to get from URL parameters
            if branch_id_param in kwargs:
                branch_id = kwargs[branch_id_param]
            # Try to get from request args
            elif branch_id_param in request.args:
                branch_id = request.args.get(branch_id_param)
            # Try to get from JSON body
            elif request.is_json and branch_id_param in request.get_json():
                branch_id = request.get_json()[branch_id_param]
            
            if not branch_id:
                return jsonify({'error': f'Branch ID ({branch_id_param}) is required'}), 400
            
            try:
                branch_id = int(branch_id)
            except ValueError:
                return jsonify({'error': 'Invalid branch ID format'}), 400
            
            # Owner has access to all branches
            if current_user.role == 'owner':
                return f(*args, **kwargs)
            
            # Check if user has access to this branch
            if not current_user.has_branch_access(branch_id):
                return jsonify({
                    'error': 'Access denied for this branch',
                    'user_branch': current_user.branch_id,
                    'requested_branch': branch_id
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_owner():
    """Decorator to require owner role"""
    return require_role('owner')

def require_manager_or_owner():
    """Decorator to require manager or owner role"""
    return require_role('owner', 'branch_manager')

def require_staff():
    """Decorator to require any staff role (not customer)"""
    return require_role('owner', 'branch_manager', 'receptionist', 'accountant')

def require_customer():
    """Decorator to require customer role"""
    return require_role('customer')

def require_receptionist_or_above():
    """Decorator to require receptionist level access or above"""
    return require_role('owner', 'branch_manager', 'receptionist')

def require_accountant_or_above():
    """Decorator to require accountant level access or above"""
    return require_role('owner', 'branch_manager', 'accountant')

def check_customer_access(customer_id_param='customer_id'):
    """Decorator to check if user can access customer data"""
    def decorator(f):
        @wraps(f)
        @jwt_required_custom
        def decorated_function(*args, **kwargs):
            current_user = kwargs.get('current_user')
            
            # Get customer_id from different sources
            customer_id = None
            
            if customer_id_param in kwargs:
                customer_id = kwargs[customer_id_param]
            elif customer_id_param in request.args:
                customer_id = request.args.get(customer_id_param)
            elif request.is_json and customer_id_param in request.get_json():
                customer_id = request.get_json()[customer_id_param]
            
            if not customer_id:
                return jsonify({'error': f'Customer ID ({customer_id_param}) is required'}), 400
            
            try:
                customer_id = int(customer_id)
            except ValueError:
                return jsonify({'error': 'Invalid customer ID format'}), 400
            
            # If user is a customer, they can only access their own data
            if current_user.role == 'customer':
                if not current_user.customer_profile or current_user.customer_profile.id != customer_id:
                    return jsonify({'error': 'Access denied - can only access own data'}), 403
            
            # Staff can access customers in their branch (owners can access all)
            elif current_user.role in ['branch_manager', 'receptionist', 'accountant']:
                from app.models.customer import Customer
                customer = Customer.query.get(customer_id)
                
                if not customer:
                    return jsonify({'error': 'Customer not found'}), 404
                
                if not current_user.has_branch_access(customer.branch_id):
                    return jsonify({'error': 'Access denied - customer not in your branch'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_api_access(f):
    """Decorator to log API access (for audit trails)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # In a production app, you might want to log to a file or database
        # For now, we'll just add the info to the response
        result = f(*args, **kwargs)
        
        # You could add logging logic here
        # Example: log user, endpoint, timestamp, etc.
        
        return result
    return decorated_function

def validate_json_request(*required_fields):
    """Decorator to validate JSON request has required fields"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Request must be JSON'}), 400
            
            data = request.get_json()
            missing_fields = [field for field in required_fields if field not in data or data[field] is None]
            
            if missing_fields:
                return jsonify({
                    'error': 'Missing required fields',
                    'missing_fields': missing_fields,
                    'required_fields': list(required_fields)
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
