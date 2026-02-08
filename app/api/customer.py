"""Customer management API routes"""
from flask import Blueprint, request, jsonify
from datetime import date, datetime
from app.database import db
from app.models.user import User
from app.models.customer import Customer, HealthReport
from app.models.branch import Branch
from app.auth import require_staff, require_receptionist_or_above, check_customer_access, validate_json_request
import secrets
import string

customer_bp = Blueprint('customer', __name__)

def generate_member_id(branch_code):
    """Generate unique member ID"""
    # Format: BranchCode + YYMMDD + 4 random digits
    today = date.today()
    date_part = today.strftime('%y%m%d')
    random_part = ''.join(secrets.choice(string.digits) for _ in range(4))
    return f"{branch_code}{date_part}{random_part}"

@customer_bp.route('/', methods=['POST'])
@require_receptionist_or_above()
@validate_json_request('username', 'email', 'password', 'first_name', 'last_name', 'branch_id')
def create_customer(current_user):
    """Create new customer"""
    data = request.get_json()
    
    # Validate branch access
    branch_id = data['branch_id']
    if not current_user.has_branch_access(branch_id):
        return jsonify({'error': 'Access denied for this branch'}), 403
    
    # Get branch for member ID generation
    branch = Branch.query.get(branch_id)
    if not branch:
        return jsonify({'error': 'Branch not found'}), 404
    
    # Check if username or email already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    try:
        # Create user account
        user = User(
            username=data['username'],
            email=data['email'],
            role='customer',
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data.get('phone'),
            branch_id=branch_id
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.flush()  # Get user ID without committing
        
        # Generate unique member ID
        member_id = generate_member_id(branch.code)
        while Customer.query.filter_by(member_id=member_id).first():
            member_id = generate_member_id(branch.code)
        
        # Create customer profile
        customer = Customer(
            user_id=user.id,
            branch_id=branch_id,
            member_id=member_id,
            date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date() if data.get('date_of_birth') else None,
            gender=data.get('gender'),
            emergency_contact_name=data.get('emergency_contact_name'),
            emergency_contact_phone=data.get('emergency_contact_phone'),
            height_cm=data.get('height_cm'),
            weight_kg=data.get('weight_kg'),
            medical_conditions=data.get('medical_conditions'),
            fitness_goals=data.get('fitness_goals')
        )
        
        db.session.add(customer)
        db.session.flush()  # Flush to get customer.id before creating health report

        # Generate initial health report if height and weight provided
        if customer.height_cm and customer.weight_kg:
            health_data = customer.generate_health_report()
            health_report = HealthReport(
                customer_id=customer.id,
                height_cm=customer.height_cm,
                weight_kg=customer.weight_kg,
                bmi=health_data['bmi'],
                bmi_category=health_data['bmi_category'],
                ideal_weight_kg=health_data['ideal_weight_kg'],
                daily_calories=health_data['daily_calories'],
                notes='Initial health assessment',
                created_by_id=current_user.id
            )
            db.session.add(health_report)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Customer created successfully',
            'customer': customer.to_dict(include_health=True),
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        print(f"Error creating customer: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to create customer', 'details': str(e)}), 500

@customer_bp.route('/', methods=['GET'])
@require_staff()
def list_customers(current_user):
    """List customers with filtering"""
    query = Customer.query.join(User)
    
    # Branch-based filtering for non-owners
    if current_user.role != 'owner':
        query = query.filter(Customer.branch_id == current_user.branch_id)
    
    # Apply filters
    branch_id = request.args.get('branch_id')
    if branch_id and current_user.has_branch_access(int(branch_id)):
        query = query.filter(Customer.branch_id == int(branch_id))
    
    is_active = request.args.get('is_active')
    if is_active is not None:
        query = query.filter(Customer.is_active == (is_active.lower() == 'true'))
    
    # Search by name or member ID
    search = request.args.get('search')
    if search:
        query = query.filter(
            db.or_(
                Customer.member_id.contains(search),
                User.first_name.contains(search),
                User.last_name.contains(search),
                User.email.contains(search),
                User.phone.contains(search)
            )
        )
    
    # Pagination
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    customers_paginated = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    customers_data = []
    for customer in customers_paginated.items:
        customer_dict = customer.to_dict()
        customer_dict['user'] = customer.user.to_dict()
        customer_dict['branch'] = customer.branch.to_dict()
        customers_data.append(customer_dict)
    
    return jsonify({
        'customers': customers_data,
        'pagination': {
            'page': page,
            'pages': customers_paginated.pages,
            'per_page': per_page,
            'total': customers_paginated.total
        }
    }), 200

@customer_bp.route('/<int:customer_id>', methods=['GET'])
@check_customer_access()
def get_customer(customer_id, current_user):
    """Get customer details"""
    customer = Customer.query.get_or_404(customer_id)
    
    customer_data = customer.to_dict(include_health=True)
    customer_data['user'] = customer.user.to_dict()
    customer_data['branch'] = customer.branch.to_dict()
    
    # Include latest health reports
    latest_reports = HealthReport.query.filter_by(
        customer_id=customer_id
    ).order_by(HealthReport.report_date.desc()).limit(5).all()
    
    customer_data['health_reports'] = [report.to_dict() for report in latest_reports]
    
    return jsonify(customer_data), 200

@customer_bp.route('/<int:customer_id>', methods=['PUT'])
@check_customer_access()
def update_customer(customer_id, current_user):
    """Update customer details"""
    customer = Customer.query.get_or_404(customer_id)
    data = request.get_json()
    
    try:
        # Update user fields
        user_fields = ['first_name', 'last_name', 'phone', 'email']
        for field in user_fields:
            if field in data and data[field] is not None:
                if field == 'email' and data[field] != customer.user.email:
                    if User.query.filter_by(email=data[field]).first():
                        return jsonify({'error': 'Email already exists'}), 400
                setattr(customer.user, field, data[field])
        
        # Update customer fields
        customer_fields = [
            'date_of_birth', 'gender', 'emergency_contact_name', 
            'emergency_contact_phone', 'height_cm', 'weight_kg', 
            'medical_conditions', 'fitness_goals'
        ]
        
        for field in customer_fields:
            if field in data and data[field] is not None:
                if field == 'date_of_birth':
                    setattr(customer, field, datetime.strptime(data[field], '%Y-%m-%d').date())
                else:
                    setattr(customer, field, data[field])
        
        # Generate new health report if height/weight updated
        if ('height_cm' in data or 'weight_kg' in data) and customer.height_cm and customer.weight_kg:
            health_data = customer.generate_health_report()
            health_report = HealthReport(
                customer_id=customer.id,
                height_cm=customer.height_cm,
                weight_kg=customer.weight_kg,
                bmi=health_data['bmi'],
                bmi_category=health_data['bmi_category'],
                ideal_weight_kg=health_data['ideal_weight_kg'],
                daily_calories=health_data['daily_calories'],
                notes='Updated measurements',
                created_by_id=current_user.id
            )
            db.session.add(health_report)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Customer updated successfully',
            'customer': customer.to_dict(include_health=True)
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update customer', 'details': str(e)}), 500

@customer_bp.route('/<int:customer_id>/health-report', methods=['POST'])
@require_receptionist_or_above()
@check_customer_access()
@validate_json_request('height_cm', 'weight_kg')
def create_health_report(customer_id, current_user):
    """Create new health report for customer"""
    customer = Customer.query.get_or_404(customer_id)
    data = request.get_json()
    
    # Update customer's current measurements
    customer.height_cm = data['height_cm']
    customer.weight_kg = data['weight_kg']
    
    # Generate health metrics
    health_data = customer.generate_health_report()
    
    # Create health report
    health_report = HealthReport(
        customer_id=customer_id,
        height_cm=data['height_cm'],
        weight_kg=data['weight_kg'],
        bmi=health_data['bmi'],
        bmi_category=health_data['bmi_category'],
        ideal_weight_kg=health_data['ideal_weight_kg'],
        daily_calories=health_data['daily_calories'],
        notes=data.get('notes', ''),
        created_by_id=current_user.id
    )
    
    try:
        db.session.add(health_report)
        db.session.commit()
        
        return jsonify({
            'message': 'Health report created successfully',
            'health_report': health_report.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create health report', 'details': str(e)}), 500

@customer_bp.route('/<int:customer_id>/health-reports', methods=['GET'])
@check_customer_access()
def get_health_reports(customer_id, current_user):
    """Get customer health report history"""
    reports = HealthReport.query.filter_by(
        customer_id=customer_id
    ).order_by(HealthReport.report_date.desc()).all()
    
    return jsonify({
        'health_reports': [report.to_dict() for report in reports],
        'total': len(reports)
    }), 200

@customer_bp.route('/<int:customer_id>/deactivate', methods=['POST'])
@require_receptionist_or_above()
@check_customer_access()
def deactivate_customer(customer_id, current_user):
    """Deactivate customer account"""
    customer = Customer.query.get_or_404(customer_id)
    
    # Check for active subscriptions
    from app.models.subscription import Subscription
    active_subscriptions = Subscription.query.filter_by(
        customer_id=customer_id,
        status='active'
    ).count()
    
    if active_subscriptions > 0:
        return jsonify({
            'error': 'Cannot deactivate customer with active subscriptions',
            'active_subscriptions': active_subscriptions
        }), 400
    
    try:
        customer.is_active = False
        customer.user.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Customer deactivated successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to deactivate customer', 'details': str(e)}), 500
