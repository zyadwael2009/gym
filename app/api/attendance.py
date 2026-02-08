"""Attendance management API routes"""
from flask import Blueprint, request, jsonify
from datetime import date, datetime, timedelta
from app.database import db
from app.models.attendance import Attendance, AttendanceValidation
from app.models.customer import Customer
from app.auth import require_staff, require_receptionist_or_above, validate_json_request

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/validate', methods=['POST'])
@require_staff()
@validate_json_request('customer_id')
def validate_entry(current_user):
    """Validate customer entry without recording"""
    data = request.get_json()
    customer_id = data['customer_id']
    branch_id = data.get('branch_id', current_user.branch_id)
    
    # Check branch access
    if not current_user.has_branch_access(branch_id):
        return jsonify({'error': 'Access denied for this branch'}), 403
    
    is_valid, reason = AttendanceValidation.validate_entry(customer_id, branch_id)
    
    return jsonify({
        'valid': is_valid,
        'reason': reason,
        'customer_id': customer_id,
        'branch_id': branch_id
    }), 200

@attendance_bp.route('/checkin', methods=['POST'])
@require_staff()
@validate_json_request('customer_id')
def record_checkin(current_user):
    """Record customer check-in"""
    data = request.get_json()
    customer_id = data['customer_id']
    branch_id = data.get('branch_id', current_user.branch_id)
    entry_method = data.get('entry_method', 'manual')
    notes = data.get('notes')
    
    # Check branch access
    if not current_user.has_branch_access(branch_id):
        return jsonify({'error': 'Access denied for this branch'}), 403
    
    # Validate customer exists
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    try:
        attendance, is_valid, reason = AttendanceValidation.record_entry(
            customer_id=customer_id,
            branch_id=branch_id,
            entry_method=entry_method,
            processed_by_id=current_user.id,
            notes=notes
        )
        
        response_data = {
            'attendance': attendance.to_dict(include_customer=True),
            'access_granted': is_valid,
            'message': reason
        }
        
        return jsonify(response_data), 201 if is_valid else 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to record attendance', 'details': str(e)}), 500

@attendance_bp.route('/checkout', methods=['POST'])
@require_staff()
@validate_json_request('attendance_id')
def record_checkout(current_user):
    """Record customer check-out"""
    data = request.get_json()
    attendance_id = data['attendance_id']
    exit_time = data.get('exit_time')  # Optional, defaults to current time
    
    attendance = Attendance.query.get_or_404(attendance_id)
    
    # Check branch access
    if not current_user.has_branch_access(attendance.branch_id):
        return jsonify({'error': 'Access denied for this attendance record'}), 403
    
    if attendance.exit_time:
        return jsonify({'error': 'Customer already checked out'}), 400
    
    try:
        if exit_time:
            from datetime import datetime
            exit_time = datetime.strptime(exit_time, '%H:%M:%S').time()
        
        success, message = attendance.mark_exit(exit_time)
        
        if success:
            db.session.commit()
            return jsonify({
                'message': message,
                'attendance': attendance.to_dict(include_customer=True)
            }), 200
        else:
            return jsonify({'error': message}), 400
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to record checkout', 'details': str(e)}), 500

@attendance_bp.route('/biometric-check', methods=['POST'])
@require_staff()
@validate_json_request('customer_id')
def biometric_check(current_user):
    """Simulate biometric verification"""
    data = request.get_json()
    customer_id = data['customer_id']
    
    # Validate customer
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    # Check branch access
    if not current_user.has_branch_access(customer.branch_id):
        return jsonify({'error': 'Access denied for customer branch'}), 403
    
    # Simulate biometric verification (in real app, this would interface with biometric device)
    import random
    biometric_success = random.choice([True, True, True, False])  # 75% success rate
    
    if biometric_success:
        # Record attendance with biometric verification
        try:
            attendance, is_valid, reason = AttendanceValidation.record_entry(
                customer_id=customer_id,
                branch_id=customer.branch_id,
                entry_method='biometric',
                processed_by_id=current_user.id,
                notes='Biometric verification successful'
            )
            
            return jsonify({
                'biometric_verified': True,
                'access_granted': is_valid,
                'message': reason,
                'attendance': attendance.to_dict(include_customer=True)
            }), 201 if is_valid else 200
        
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to record attendance', 'details': str(e)}), 500
    else:
        return jsonify({
            'biometric_verified': False,
            'access_granted': False,
            'message': 'Biometric verification failed'
        }), 200

@attendance_bp.route('/', methods=['GET'])
@require_staff()
def list_attendance(current_user):
    """List attendance records with filtering"""
    query = Attendance.query.join(Customer)
    
    # Branch-based filtering for non-owners
    if current_user.role != 'owner':
        query = query.filter(Attendance.branch_id == current_user.branch_id)
    
    # Apply filters
    branch_id = request.args.get('branch_id')
    if branch_id and current_user.has_branch_access(int(branch_id)):
        query = query.filter(Attendance.branch_id == int(branch_id))
    
    customer_id = request.args.get('customer_id')
    if customer_id:
        query = query.filter(Attendance.customer_id == int(customer_id))
    
    # Date filters
    start_date = request.args.get('start_date')
    if start_date:
        query = query.filter(Attendance.entry_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    
    end_date = request.args.get('end_date')
    if end_date:
        query = query.filter(Attendance.entry_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    else:
        # Default to last 30 days
        query = query.filter(Attendance.entry_date >= date.today() - timedelta(days=30))
    
    access_granted = request.args.get('access_granted')
    if access_granted is not None:
        query = query.filter(Attendance.access_granted == (access_granted.lower() == 'true'))
    
    # Pagination
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    
    attendance_paginated = query.order_by(Attendance.entry_date.desc(), Attendance.entry_time.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    attendance_data = []
    for attendance in attendance_paginated.items:
        attendance_dict = attendance.to_dict(include_customer=True)
        attendance_data.append(attendance_dict)
    
    return jsonify({
        'attendance': attendance_data,
        'pagination': {
            'page': page,
            'pages': attendance_paginated.pages,
            'per_page': per_page,
            'total': attendance_paginated.total
        }
    }), 200

@attendance_bp.route('/today', methods=['GET'])
@require_staff()
def today_attendance(current_user):
    """Get today's attendance for quick overview"""
    query = Attendance.query.filter(Attendance.entry_date == date.today())
    
    # Branch filtering for non-owners
    if current_user.role != 'owner':
        query = query.filter(Attendance.branch_id == current_user.branch_id)
    
    branch_id = request.args.get('branch_id')
    if branch_id and current_user.has_branch_access(int(branch_id)):
        query = query.filter(Attendance.branch_id == int(branch_id))
    
    attendance_records = query.order_by(Attendance.entry_time.desc()).all()
    
    # Separate checked in vs checked out
    checked_in = [a for a in attendance_records if a.access_granted and not a.exit_time]
    checked_out = [a for a in attendance_records if a.access_granted and a.exit_time]
    denied_entry = [a for a in attendance_records if not a.access_granted]
    
    return jsonify({
        'date': date.today().isoformat(),
        'summary': {
            'total_entries': len([a for a in attendance_records if a.access_granted]),
            'currently_in_gym': len(checked_in),
            'checked_out': len(checked_out),
            'denied_entries': len(denied_entry)
        },
        'currently_in_gym': [a.to_dict(include_customer=True) for a in checked_in],
        'recent_entries': [a.to_dict(include_customer=True) for a in attendance_records[:10]]
    }), 200

@attendance_bp.route('/customer/<int:customer_id>/history', methods=['GET'])
@require_staff()
def customer_attendance_history(customer_id, current_user):
    """Get attendance history for specific customer"""
    customer = Customer.query.get_or_404(customer_id)
    
    # Check branch access
    if not current_user.has_branch_access(customer.branch_id):
        return jsonify({'error': 'Access denied for customer branch'}), 403
    
    # Date range (default last 90 days)
    days_back = int(request.args.get('days', 90))
    start_date = date.today() - timedelta(days=days_back)
    
    attendance_records = Attendance.query.filter(
        Attendance.customer_id == customer_id,
        Attendance.entry_date >= start_date,
        Attendance.access_granted == True
    ).order_by(Attendance.entry_date.desc(), Attendance.entry_time.desc()).all()
    
    # Calculate statistics
    total_visits = len(attendance_records)
    avg_duration = 0
    if attendance_records:
        durations = [a.calculate_duration() for a in attendance_records if a.calculate_duration()]
        if durations:
            avg_duration = sum(durations) / len(durations)
    
    # Monthly breakdown
    monthly_visits = {}
    for attendance in attendance_records:
        month_key = attendance.entry_date.strftime('%Y-%m')
        if month_key not in monthly_visits:
            monthly_visits[month_key] = 0
        monthly_visits[month_key] += 1
    
    return jsonify({
        'customer': {
            'id': customer.id,
            'member_id': customer.member_id,
            'name': f"{customer.user.first_name} {customer.user.last_name}"
        },
        'statistics': {
            'total_visits': total_visits,
            'days_period': days_back,
            'average_duration_minutes': round(avg_duration, 1) if avg_duration else 0,
            'visits_per_month': monthly_visits
        },
        'attendance_history': [a.to_dict() for a in attendance_records]
    }), 200
