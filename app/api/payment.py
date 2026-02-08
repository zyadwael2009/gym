"""Payment management API routes"""
from flask import Blueprint, request, jsonify
from datetime import date, datetime
from app.database import db
from app.models.payment import Payment, PaymentAuditLog
from app.models.subscription import Subscription
from app.models.customer import Customer
from app.auth import require_staff, require_accountant_or_above, validate_json_request
import secrets
import string

payment_bp = Blueprint('payment', __name__)

def generate_payment_number():
    """Generate unique payment number"""
    today = date.today()
    date_part = today.strftime('%y%m%d')
    random_part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    return f"PAY{date_part}{random_part}"

@payment_bp.route('/', methods=['POST'])
@require_staff()
@validate_json_request('customer_id', 'amount', 'payment_method')
def create_payment(current_user):
    """Create new payment"""
    data = request.get_json()
    
    # Validate customer
    customer = Customer.query.get(data['customer_id'])
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    # Check branch access
    if not current_user.has_branch_access(customer.branch_id):
        return jsonify({'error': 'Access denied for customer branch'}), 403
    
    # Validate subscription if provided
    subscription = None
    if data.get('subscription_id'):
        subscription = Subscription.query.get(data['subscription_id'])
        if not subscription or subscription.customer_id != customer.id:
            return jsonify({'error': 'Invalid subscription for this customer'}), 400
    
    # Generate payment number
    payment_number = generate_payment_number()
    while Payment.query.filter_by(payment_number=payment_number).first():
        payment_number = generate_payment_number()
    
    # Create payment
    payment = Payment(
        payment_number=payment_number,
        amount=data['amount'],
        payment_method=data['payment_method'],
        customer_id=data['customer_id'],
        subscription_id=data.get('subscription_id'),
        branch_id=customer.branch_id,
        service_type=data.get('service_type', 'subscription'),
        description=data.get('description'),
        reference_number=data.get('reference_number'),
        processed_by_id=current_user.id
    )
    
    try:
        db.session.add(payment)
        db.session.flush()  # Get payment ID
        
        # Create audit log
        audit_log = PaymentAuditLog(
            payment_id=payment.id,
            action='created',
            old_status=None,
            new_status='pending',
            performed_by_id=current_user.id,
            notes=f"Payment created for {payment.service_type}"
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Payment created successfully',
            'payment': payment.to_dict(include_customer=True, include_subscription=True)
        }), 201
    
    except Exception as e:
        db.session.rollback()
        print(f"Error creating payment: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to create payment', 'details': str(e)}), 500

@payment_bp.route('/<int:payment_id>/process', methods=['POST'])
@require_staff()
def process_payment(payment_id, current_user):
    """Process/complete payment"""
    payment = Payment.query.get_or_404(payment_id)
    
    # Check branch access
    if not current_user.has_branch_access(payment.branch_id):
        return jsonify({'error': 'Access denied for this payment'}), 403
    
    old_status = payment.status
    success, message = payment.process_payment()
    
    if success:
        # Create audit log
        audit_log = PaymentAuditLog(
            payment_id=payment.id,
            action='processed',
            old_status=old_status,
            new_status=payment.status,
            performed_by_id=current_user.id,
            notes="Payment processed and completed"
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'message': message,
            'payment': payment.to_dict(include_customer=True, include_subscription=True)
        }), 200
    else:
        return jsonify({'error': message}), 400

@payment_bp.route('/', methods=['GET'])
@require_staff()
def list_payments(current_user):
    """List payments with filtering"""
    query = Payment.query.join(Customer)
    
    # Branch-based filtering for non-owners
    if current_user.role != 'owner':
        query = query.filter(Payment.branch_id == current_user.branch_id)
    
    # Apply filters
    branch_id = request.args.get('branch_id')
    if branch_id and current_user.has_branch_access(int(branch_id)):
        query = query.filter(Payment.branch_id == int(branch_id))
    
    status = request.args.get('status')
    if status:
        query = query.filter(Payment.status == status)
    
    payment_method = request.args.get('payment_method')
    if payment_method:
        query = query.filter(Payment.payment_method == payment_method)
    
    service_type = request.args.get('service_type')
    if service_type:
        query = query.filter(Payment.service_type == service_type)
    
    # Date filters
    start_date = request.args.get('start_date')
    if start_date:
        query = query.filter(Payment.payment_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    
    end_date = request.args.get('end_date')
    if end_date:
        query = query.filter(Payment.payment_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    # Pagination
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    payments_paginated = query.order_by(Payment.payment_time.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    payments_data = []
    for payment in payments_paginated.items:
        payment_dict = payment.to_dict(include_customer=True, include_subscription=True)
        payments_data.append(payment_dict)
    
    return jsonify({
        'payments': payments_data,
        'pagination': {
            'page': page,
            'pages': payments_paginated.pages,
            'per_page': per_page,
            'total': payments_paginated.total
        }
    }), 200

@payment_bp.route('/<int:payment_id>', methods=['GET'])
@require_staff()
def get_payment(payment_id, current_user):
    """Get payment details"""
    payment = Payment.query.get_or_404(payment_id)
    
    # Check branch access
    if not current_user.has_branch_access(payment.branch_id):
        return jsonify({'error': 'Access denied for this payment'}), 403
    
    payment_data = payment.to_dict(include_customer=True, include_subscription=True)
    
    # Include audit logs
    audit_logs = PaymentAuditLog.query.filter_by(
        payment_id=payment_id
    ).order_by(PaymentAuditLog.timestamp.desc()).all()
    
    payment_data['audit_logs'] = [log.to_dict() for log in audit_logs]
    
    return jsonify(payment_data), 200

@payment_bp.route('/<int:payment_id>/refund', methods=['POST'])
@require_accountant_or_above()
def refund_payment(payment_id, current_user):
    """Process payment refund"""
    payment = Payment.query.get_or_404(payment_id)
    data = request.get_json() or {}
    
    # Check branch access
    if not current_user.has_branch_access(payment.branch_id):
        return jsonify({'error': 'Access denied for this payment'}), 403
    
    reason = data.get('reason', 'Customer request')
    old_status = payment.status
    
    success, message = payment.refund_payment(reason, current_user.id)
    
    if success:
        # Create audit log
        audit_log = PaymentAuditLog(
            payment_id=payment.id,
            action='refunded',
            old_status=old_status,
            new_status=payment.status,
            performed_by_id=current_user.id,
            notes=f"Payment refunded: {reason}"
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'message': message,
            'payment': payment.to_dict(include_customer=True, include_subscription=True)
        }), 200
    else:
        return jsonify({'error': message}), 400

@payment_bp.route('/summary', methods=['GET'])
@require_accountant_or_above()
def payment_summary(current_user):
    """Get payment summary for date range"""
    # Default to current month
    today = date.today()
    start_date = request.args.get('start_date')
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date = today.replace(day=1)
    
    end_date = request.args.get('end_date')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        end_date = today
    
    # Base query
    query = Payment.query.filter(
        Payment.payment_date >= start_date,
        Payment.payment_date <= end_date
    )
    
    # Branch filtering for non-owners
    if current_user.role != 'owner':
        query = query.filter(Payment.branch_id == current_user.branch_id)
    
    branch_id = request.args.get('branch_id')
    if branch_id and current_user.has_branch_access(int(branch_id)):
        query = query.filter(Payment.branch_id == int(branch_id))
    
    payments = query.all()
    
    # Calculate summary
    total_amount = sum(p.amount for p in payments if p.status == 'completed')
    total_refunded = sum(p.amount for p in payments if p.status == 'refunded')
    net_amount = total_amount - total_refunded
    
    # Group by payment method
    payment_methods = {}
    for payment in payments:
        if payment.status == 'completed':
            method = payment.payment_method
            if method not in payment_methods:
                payment_methods[method] = {'count': 0, 'amount': 0}
            payment_methods[method]['count'] += 1
            payment_methods[method]['amount'] += float(payment.amount)
    
    # Group by service type
    service_types = {}
    for payment in payments:
        if payment.status == 'completed':
            service = payment.service_type or 'other'
            if service not in service_types:
                service_types[service] = {'count': 0, 'amount': 0}
            service_types[service]['count'] += 1
            service_types[service]['amount'] += float(payment.amount)
    
    return jsonify({
        'summary': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_payments': len([p for p in payments if p.status == 'completed']),
            'total_amount': float(total_amount),
            'total_refunded': float(total_refunded),
            'net_amount': float(net_amount),
            'pending_payments': len([p for p in payments if p.status == 'pending']),
            'failed_payments': len([p for p in payments if p.status == 'failed'])
        },
        'by_payment_method': payment_methods,
        'by_service_type': service_types
    }), 200
