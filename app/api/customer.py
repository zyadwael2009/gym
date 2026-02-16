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

# Customer App Specific Endpoints

@customer_bp.route('/generate-qr', methods=['POST'])
def generate_qr():
    """Generate QR code for customer attendance"""
    from flask_jwt_extended import jwt_required, get_jwt_identity
    import json
    import time
    import random
    
    @jwt_required()
    def _generate_qr():
        current_identity = get_jwt_identity()
        
        # Extract customer ID from JWT identity (format: "customer_123")
        if not current_identity.startswith('customer_'):
            return jsonify({'error': 'Invalid token', 'message': 'رمز غير صحيح'}), 401
        
        customer_id = int(current_identity.split('_')[1])
        customer = Customer.query.get(customer_id)
        
        if not customer:
            return jsonify({'error': 'Customer not found', 'message': 'العميل غير موجود'}), 404
        
        # Get QR data from request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided', 'message': 'لا توجد بيانات'}), 400
        
        # Store QR session in database or cache (for production use Redis)
        # For now, just return the QR data
        qr_data = {
            'customer_id': customer.id,
            'customer_name': customer.name,
            'customer_email': customer.email,
            'session_id': data.get('session_id'),
            'generated_at': data.get('generated_at'),
            'expires_at': data.get('expires_at'),
            'type': 'customer_attendance'
        }
        
        return jsonify({
            'qr_code': json.dumps(qr_data),
            'message': 'تم إنتاج رمز QR بنجاح'
        }), 200
    
    return _generate_qr()

@customer_bp.route('/mark-attendance', methods=['POST'])
def mark_attendance():
    """Mark customer attendance"""
    from flask_jwt_extended import jwt_required, get_jwt_identity
    from app.models.attendance import Attendance
    
    @jwt_required()
    def _mark_attendance():
        current_identity = get_jwt_identity()
        
        # Extract customer ID from JWT identity
        if not current_identity.startswith('customer_'):
            return jsonify({'error': 'Invalid token', 'message': 'رمز غير صحيح'}), 401
        
        customer_id = int(current_identity.split('_')[1])
        customer = Customer.query.get(customer_id)
        
        if not customer:
            return jsonify({'error': 'Customer not found', 'message': 'العميل غير موجود'}), 404
        
        data = request.get_json()
        attendance_date = data.get('date', datetime.now().isoformat())
        
        # Parse the date
        try:
            if isinstance(attendance_date, str):
                attendance_date = datetime.fromisoformat(attendance_date.replace('Z', '+00:00'))
        except:
            attendance_date = datetime.now()
        
        # Check if already attended today
        today = attendance_date.date()
        existing_attendance = Attendance.query.filter(
            Attendance.customer_id == customer_id,
            Attendance.check_in_time >= datetime.combine(today, datetime.min.time()),
            Attendance.check_in_time < datetime.combine(today, datetime.max.time())
        ).first()
        
        if existing_attendance:
            return jsonify({
                'error': 'Already attended today',
                'message': 'تم تسجيل الحضور مسبقاً اليوم'
            }), 400
        
        try:
            # Create attendance record
            attendance = Attendance(
                customer_id=customer_id,
                check_in_time=attendance_date,
                branch_id=customer.branch_id or 1  # Default to branch 1 if no branch set
            )
            db.session.add(attendance)
            
            # Update customer's last attendance
            customer.last_attendance = attendance_date
            db.session.commit()
            
            return jsonify({
                'message': 'تم تسجيل الحضور بنجاح',
                'attendance': {
                    'id': attendance.id,
                    'check_in_time': attendance.check_in_time.isoformat(),
                    'date': attendance.check_in_time.date().isoformat()
                }
            }), 201
        
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'error': 'Failed to mark attendance',
                'message': f'فشل في تسجيل الحضور: {str(e)}'
            }), 500
    
    return _mark_attendance()

@customer_bp.route('/mark-attendance-qr', methods=['POST'])
@require_receptionist_or_above()
@validate_json_request('customer_id', 'qr_timestamp')
def mark_attendance_by_qr(current_user):
    """Mark customer attendance by scanning QR code (staff only)"""
    from app.models.attendance import Attendance
    import json
    
    data = request.get_json()
    customer_id = data['customer_id']
    qr_timestamp = data['qr_timestamp']
    
    # Get customer
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({
            'error': 'Customer not found',
            'message': 'العميل غير موجود'
        }), 404
    
    # Verify staff has access to customer's branch
    if not current_user.has_branch_access(customer.branch_id):
        return jsonify({
            'error': 'Access denied for this branch',
            'message': 'غير مسموح الوصول لهذا الفرع'
        }), 403
    
    # Validate QR timestamp (should be within last 5 minutes)
    try:
        # Handle both ISO format strings and millisecond timestamps
        if isinstance(qr_timestamp, (int, float)):
            # Milliseconds timestamp from Flutter
            qr_time = datetime.fromtimestamp(qr_timestamp / 1000.0)
        elif isinstance(qr_timestamp, str):
            # ISO format string
            qr_time = datetime.fromisoformat(qr_timestamp.replace('Z', '+00:00'))
        else:
            raise ValueError("Invalid timestamp type")
        
        time_diff = (datetime.now() - qr_time).total_seconds()
        
        # QR code expires after 5 minutes
        if time_diff > 300:
            return jsonify({
                'error': 'QR code expired',
                'message': 'انتهت صلاحية رمز QR'
            }), 400
        
        if time_diff < -60:  # Future timestamp
            return jsonify({
                'error': 'Invalid QR code',
                'message': 'رمز QR غير صالح'
            }), 400
    except Exception as e:
        return jsonify({
            'error': 'Invalid timestamp format',
            'message': 'صيغة الوقت غير صحيحة'
        }), 400
    
    # Check if already attended today
    today = datetime.now().date()
    existing_attendance = Attendance.query.filter(
        Attendance.customer_id == customer_id,
        Attendance.entry_date == today
    ).first()
    
    if existing_attendance:
        return jsonify({
            'error': 'Already attended today',
            'message': 'تم تسجيل الحضور مسبقاً اليوم',
            'customer_name': f"{customer.user.first_name} {customer.user.last_name}",
            'check_in_time': existing_attendance.entry_time.strftime('%I:%M %p')
        }), 400
    
    try:
        # Create attendance record
        now = datetime.now()
        print(f"DEBUG: Creating attendance for customer {customer_id}")
        print(f"DEBUG: Branch ID: {customer.branch_id}")
        print(f"DEBUG: Current user ID: {current_user.id}")
        print(f"DEBUG: Entry date: {now.date()}, Entry time: {now.time()}")
        
        attendance = Attendance(
            customer_id=customer_id,
            entry_date=now.date(),
            entry_time=now.time(),
            branch_id=customer.branch_id,
            entry_method='manual',  # QR code scan
            processed_by_id=current_user.id  # Track who marked the attendance
        )
        db.session.add(attendance)
        print(f"DEBUG: Before commit")
        db.session.commit()
        print(f"DEBUG: After commit - Attendance ID: {attendance.id}")
        
        customer_name = f"{customer.user.first_name} {customer.user.last_name}"
        check_in_time = attendance.entry_time.strftime('%I:%M %p')
        
        return jsonify({
            'message': 'تم تسجيل الحضور بنجاح',
            'customer_name': customer_name,
            'check_in_time': check_in_time,
            'member_id': customer.member_id,
            'attendance': {
                'id': attendance.id,
                'entry_date': attendance.entry_date.isoformat(),
                'entry_time': attendance.entry_time.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"DEBUG: Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to mark attendance',
            'message': f'فشل في تسجيل الحضور: {str(e)}'
        }), 500

@customer_bp.route('/<int:customer_id>/attendance', methods=['GET'])
def get_customer_attendance(customer_id):
    """Get customer attendance history"""
    from flask_jwt_extended import jwt_required, get_jwt_identity
    from app.models.attendance import Attendance
    from datetime import datetime, timedelta
    
    @jwt_required()
    def _get_attendance():
        current_identity = get_jwt_identity()
        
        # Extract customer ID from JWT identity
        if not current_identity.startswith('customer_'):
            return jsonify({'error': 'Invalid token', 'message': 'رمز غير صحيح'}), 401
        
        token_customer_id = int(current_identity.split('_')[1])
        
        # Ensure customer can only access their own data
        if token_customer_id != customer_id:
            return jsonify({'error': 'Access denied', 'message': 'غير مسموح الوصول'}), 403
        
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({'error': 'Customer not found', 'message': 'العميل غير موجود'}), 404
        
        # Get attendance records (last 90 days)
        start_date = datetime.now().date() - timedelta(days=90)
        attendance_records = Attendance.query.filter(
            Attendance.customer_id == customer_id,
            Attendance.entry_date >= start_date,
            Attendance.access_granted == True
        ).order_by(Attendance.entry_date.desc(), Attendance.entry_time.desc()).limit(100).all()
        
        attendance_list = []
        for record in attendance_records:
            # Combine date and time for proper datetime
            entry_datetime = datetime.combine(record.entry_date, record.entry_time)
            exit_datetime = None
            if record.exit_time:
                exit_datetime = datetime.combine(record.entry_date, record.exit_time)
            
            attendance_list.append({
                'id': record.id,
                'date': record.entry_date.isoformat(),
                'entry_date': record.entry_date.isoformat(),
                'entry_time': record.entry_time.strftime('%H:%M') if record.entry_time else None,
                'exit_time': record.exit_time.strftime('%H:%M') if record.exit_time else None,
                'entry_datetime': entry_datetime.isoformat(),
                'exit_datetime': exit_datetime.isoformat() if exit_datetime else None,
                'branch_id': record.branch_id,
                'duration_minutes': record.calculate_duration() if record.exit_time else None
            })
        
        return jsonify({
            'attendance': attendance_list,
            'total': len(attendance_list),
            'message': 'تم جلب تاريخ الحضور بنجاح'
        }), 200
    
    return _get_attendance()

@customer_bp.route('/profile', methods=['PUT'])
def update_customer_profile():
    """Update customer profile"""
    from flask_jwt_extended import jwt_required, get_jwt_identity
    
    @jwt_required()
    def _update_profile():
        current_identity = get_jwt_identity()
        
        # Extract customer ID from JWT identity
        if not current_identity.startswith('customer_'):
            return jsonify({'error': 'Invalid token', 'message': 'رمز غير صحيح'}), 401
        
        customer_id = int(current_identity.split('_')[1])
        customer = Customer.query.get(customer_id)
        
        if not customer:
            return jsonify({'error': 'Customer not found', 'message': 'العميل غير موجود'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided', 'message': 'لا توجد بيانات'}), 400
        
        try:
            # Update customer fields
            if 'name' in data:
                customer.name = data['name']
            if 'email' in data:
                customer.email = data['email']
            if 'phone' in data:
                customer.phone = data['phone']
            if 'address' in data:
                customer.address = data['address']
            if 'emergency_contact' in data:
                customer.emergency_contact = data['emergency_contact']
            
            customer.updated_at = datetime.now()
            db.session.commit()
            
            return jsonify({
                'message': 'تم تحديث الملف الشخصي بنجاح',
                'customer': customer.to_dict()
            }), 200
        
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'error': 'Failed to update profile',
                'message': f'فشل في تحديث الملف الشخصي: {str(e)}'
            }), 500
    
    return _update_profile()
