"""Subscription management API routes"""
from flask import Blueprint, request, jsonify
from datetime import date, datetime, timedelta
from app.database import db
from app.models.subscription import SubscriptionPlan, Subscription, SubscriptionFreeze
from app.models.customer import Customer
from app.models.branch import Branch
from app.auth import require_staff, require_receptionist_or_above, require_owner, validate_json_request
import secrets
import string

subscription_bp = Blueprint('subscription', __name__)

def generate_subscription_number(branch_code):
    """Generate unique subscription number"""
    today = date.today()
    date_part = today.strftime('%y%m%d')
    random_part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    return f"SUB{branch_code}{date_part}{random_part}"

# Subscription Plans
@subscription_bp.route('/plans', methods=['GET'])
@require_staff()
def list_subscription_plans(current_user):
    """List all subscription plans"""
    plans = SubscriptionPlan.query.filter_by(is_active=True).all()
    
    return jsonify({
        'plans': [plan.to_dict() for plan in plans],
        'total': len(plans)
    }), 200

@subscription_bp.route('/plans', methods=['POST'])
@require_owner()
@validate_json_request('name', 'duration_days', 'price')
def create_subscription_plan(current_user):
    """Create new subscription plan"""
    data = request.get_json()
    
    plan = SubscriptionPlan(
        name=data['name'],
        description=data.get('description'),
        duration_days=data['duration_days'],
        price=data['price'],
        access_hours=data.get('access_hours'),
        includes_trainer=data.get('includes_trainer', False),
        includes_nutrition=data.get('includes_nutrition', False),
        max_freeze_days=data.get('max_freeze_days', 0)
    )
    
    try:
        db.session.add(plan)
        db.session.commit()
        
        return jsonify({
            'message': 'Subscription plan created successfully',
            'plan': plan.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create plan', 'details': str(e)}), 500

@subscription_bp.route('/plans/<int:plan_id>', methods=['PUT'])
@require_owner()
def update_subscription_plan(plan_id, current_user):
    """Update subscription plan"""
    plan = SubscriptionPlan.query.get_or_404(plan_id)
    data = request.get_json()
    
    updatable_fields = [
        'name', 'description', 'duration_days', 'price', 
        'access_hours', 'includes_trainer', 'includes_nutrition', 
        'max_freeze_days', 'is_active'
    ]
    
    for field in updatable_fields:
        if field in data and data[field] is not None:
            setattr(plan, field, data[field])
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Plan updated successfully',
            'plan': plan.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update plan', 'details': str(e)}), 500

# Subscriptions
@subscription_bp.route('/', methods=['POST'])
@require_receptionist_or_above()
@validate_json_request('customer_id', 'plan_id', 'start_date')
def create_subscription(current_user):
    """Create new subscription"""
    data = request.get_json()
    
    # Validate customer
    customer = Customer.query.get(data['customer_id'])
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    # Check branch access
    if not current_user.has_branch_access(customer.branch_id):
        return jsonify({'error': 'Access denied for customer branch'}), 403
    
    # Validate plan
    plan = SubscriptionPlan.query.get(data['plan_id'])
    if not plan or not plan.is_active:
        return jsonify({'error': 'Plan not found or inactive'}), 404
    
    # Calculate dates
    start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    end_date = start_date + timedelta(days=plan.duration_days)
    
    # Generate subscription number
    branch = Branch.query.get(customer.branch_id)
    subscription_number = generate_subscription_number(branch.code)
    while Subscription.query.filter_by(subscription_number=subscription_number).first():
        subscription_number = generate_subscription_number(branch.code)
    
    # Create subscription
    subscription = Subscription(
        customer_id=data['customer_id'],
        plan_id=data['plan_id'],
        branch_id=customer.branch_id,
        subscription_number=subscription_number,
        start_date=start_date,
        end_date=end_date,
        actual_price=data.get('actual_price', plan.price),
        auto_renew=data.get('auto_renew', False),
        created_by_id=current_user.id
    )
    
    try:
        db.session.add(subscription)
        db.session.commit()
        
        return jsonify({
            'message': 'Subscription created successfully (pending payment)',
            'subscription': subscription.to_dict(include_details=True)
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create subscription', 'details': str(e)}), 500

@subscription_bp.route('/', methods=['GET'])
@require_staff()
def list_subscriptions(current_user):
    """List subscriptions with filtering"""
    query = Subscription.query.join(Customer)
    
    # Branch-based filtering for non-owners
    if current_user.role != 'owner':
        query = query.filter(Subscription.branch_id == current_user.branch_id)
    
    # Apply filters
    branch_id = request.args.get('branch_id')
    if branch_id and current_user.has_branch_access(int(branch_id)):
        query = query.filter(Subscription.branch_id == int(branch_id))
    
    status = request.args.get('status')
    if status:
        query = query.filter(Subscription.status == status)
    
    customer_id = request.args.get('customer_id')
    if customer_id:
        query = query.filter(Subscription.customer_id == int(customer_id))
    
    # Date filters
    start_date = request.args.get('start_date')
    if start_date:
        query = query.filter(Subscription.start_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    
    end_date = request.args.get('end_date')
    if end_date:
        query = query.filter(Subscription.end_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    # Pagination
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    subscriptions_paginated = query.order_by(Subscription.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    subscriptions_data = []
    for subscription in subscriptions_paginated.items:
        sub_dict = subscription.to_dict(include_details=True)
        sub_dict['customer'] = {
            'member_id': subscription.customer.member_id,
            'name': f"{subscription.customer.user.first_name} {subscription.customer.user.last_name}"
        }
        subscriptions_data.append(sub_dict)
    
    return jsonify({
        'subscriptions': subscriptions_data,
        'pagination': {
            'page': page,
            'pages': subscriptions_paginated.pages,
            'per_page': per_page,
            'total': subscriptions_paginated.total
        }
    }), 200

@subscription_bp.route('/<int:subscription_id>', methods=['GET'])
@require_staff()
def get_subscription(subscription_id, current_user):
    """Get subscription details"""
    subscription = Subscription.query.get_or_404(subscription_id)
    
    # Check branch access
    if not current_user.has_branch_access(subscription.branch_id):
        return jsonify({'error': 'Access denied for this subscription'}), 403
    
    sub_data = subscription.to_dict(include_details=True)
    sub_data['customer'] = subscription.customer.to_dict()
    sub_data['customer']['user'] = subscription.customer.user.to_dict()
    sub_data['payments'] = [payment.to_dict() for payment in subscription.payments]
    sub_data['freeze_history'] = [freeze.to_dict() for freeze in subscription.freeze_history]
    
    return jsonify(sub_data), 200

@subscription_bp.route('/<int:subscription_id>/activate', methods=['POST'])
@require_receptionist_or_above()
def activate_subscription(subscription_id, current_user):
    """Manually activate subscription (if payment is complete)"""
    subscription = Subscription.query.get_or_404(subscription_id)
    
    # Check branch access
    if not current_user.has_branch_access(subscription.branch_id):
        return jsonify({'error': 'Access denied for this subscription'}), 403
    
    success, message = subscription.activate_subscription()
    
    if success:
        db.session.commit()
        return jsonify({
            'message': message,
            'subscription': subscription.to_dict(include_details=True)
        }), 200
    else:
        return jsonify({'error': message}), 400

@subscription_bp.route('/<int:subscription_id>/freeze', methods=['POST'])
@require_receptionist_or_above()
@validate_json_request('days')
def freeze_subscription(subscription_id, current_user):
    """Freeze subscription"""
    subscription = Subscription.query.get_or_404(subscription_id)
    data = request.get_json()
    
    # Check branch access
    if not current_user.has_branch_access(subscription.branch_id):
        return jsonify({'error': 'Access denied for this subscription'}), 403
    
    days = data['days']
    reason = data.get('reason', 'Customer request')
    
    success, message = subscription.freeze_subscription(days, reason)
    
    if success:
        # Create freeze history record
        freeze_record = SubscriptionFreeze(
            subscription_id=subscription_id,
            freeze_start=subscription.current_freeze_start,
            freeze_end=subscription.current_freeze_end,
            days_frozen=days,
            reason=reason,
            created_by_id=current_user.id
        )
        db.session.add(freeze_record)
        db.session.commit()
        
        return jsonify({
            'message': message,
            'subscription': subscription.to_dict(include_details=True)
        }), 200
    else:
        return jsonify({'error': message}), 400

@subscription_bp.route('/<int:subscription_id>/unfreeze', methods=['POST'])
@require_receptionist_or_above()
def unfreeze_subscription(subscription_id, current_user):
    """Resume frozen subscription"""
    subscription = Subscription.query.get_or_404(subscription_id)
    
    # Check branch access
    if not current_user.has_branch_access(subscription.branch_id):
        return jsonify({'error': 'Access denied for this subscription'}), 403
    
    success, message = subscription.unfreeze_subscription()
    
    if success:
        db.session.commit()
        return jsonify({
            'message': message,
            'subscription': subscription.to_dict(include_details=True)
        }), 200
    else:
        return jsonify({'error': message}), 400

@subscription_bp.route('/<int:subscription_id>/cancel', methods=['POST'])
@require_receptionist_or_above()
def cancel_subscription(subscription_id, current_user):
    """Cancel subscription"""
    subscription = Subscription.query.get_or_404(subscription_id)
    data = request.get_json() or {}
    
    # Check branch access
    if not current_user.has_branch_access(subscription.branch_id):
        return jsonify({'error': 'Access denied for this subscription'}), 403
    
    reason = data.get('reason', 'Customer request')
    
    success, message = subscription.cancel_subscription(reason)
    
    if success:
        db.session.commit()
        return jsonify({
            'message': message,
            'subscription': subscription.to_dict(include_details=True)
        }), 200
    else:
        return jsonify({'error': message}), 400

@subscription_bp.route('/<int:subscription_id>/renew', methods=['POST'])
@require_receptionist_or_above()
def renew_subscription(subscription_id, current_user):
    """Renew subscription (create new subscription)"""
    old_subscription = Subscription.query.get_or_404(subscription_id)
    data = request.get_json() or {}
    
    # Check branch access
    if not current_user.has_branch_access(old_subscription.branch_id):
        return jsonify({'error': 'Access denied for this subscription'}), 403
    
    # Get plan (use same plan or new one)
    plan_id = data.get('plan_id', old_subscription.plan_id)
    plan = SubscriptionPlan.query.get(plan_id)
    if not plan or not plan.is_active:
        return jsonify({'error': 'Plan not found or inactive'}), 404
    
    # Calculate new dates
    start_date = data.get('start_date')
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date = max(date.today(), old_subscription.end_date + timedelta(days=1))
    
    end_date = start_date + timedelta(days=plan.duration_days)
    
    # Generate new subscription number
    branch = Branch.query.get(old_subscription.branch_id)
    subscription_number = generate_subscription_number(branch.code)
    while Subscription.query.filter_by(subscription_number=subscription_number).first():
        subscription_number = generate_subscription_number(branch.code)
    
    # Create new subscription
    new_subscription = Subscription(
        customer_id=old_subscription.customer_id,
        plan_id=plan_id,
        branch_id=old_subscription.branch_id,
        subscription_number=subscription_number,
        start_date=start_date,
        end_date=end_date,
        actual_price=data.get('actual_price', plan.price),
        auto_renew=data.get('auto_renew', old_subscription.auto_renew),
        created_by_id=current_user.id
    )
    
    try:
        db.session.add(new_subscription)
        db.session.commit()
        
        return jsonify({
            'message': 'Subscription renewed successfully (pending payment)',
            'new_subscription': new_subscription.to_dict(include_details=True),
            'old_subscription_id': subscription_id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to renew subscription', 'details': str(e)}), 500

@subscription_bp.route('/expiring', methods=['GET'])
@require_staff()
def get_expiring_subscriptions(current_user):
    """Get subscriptions expiring soon"""
    days_ahead = int(request.args.get('days', 7))
    cutoff_date = date.today() + timedelta(days=days_ahead)
    
    query = Subscription.query.filter(
        Subscription.status == 'active',
        Subscription.end_date <= cutoff_date,
        Subscription.end_date >= date.today()
    )
    
    # Branch-based filtering for non-owners
    if current_user.role != 'owner':
        query = query.filter(Subscription.branch_id == current_user.branch_id)
    
    subscriptions = query.order_by(Subscription.end_date.asc()).all()
    
    subscriptions_data = []
    for subscription in subscriptions:
        sub_dict = subscription.to_dict(include_details=True)
        sub_dict['customer'] = {
            'member_id': subscription.customer.member_id,
            'name': f"{subscription.customer.user.first_name} {subscription.customer.user.last_name}",
            'phone': subscription.customer.user.phone
        }
        subscriptions_data.append(sub_dict)
    
    return jsonify({
        'expiring_subscriptions': subscriptions_data,
        'total': len(subscriptions),
        'days_ahead': days_ahead
    }), 200
