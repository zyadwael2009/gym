"""Complaint management API routes"""
from flask import Blueprint, request, jsonify
from datetime import date, datetime
from app.database import db
from app.models.complaint import Complaint, ComplaintUpdate
from app.models.customer import Customer
from app.models.user import User
from app.auth import require_staff, require_manager_or_owner, validate_json_request
import secrets
import string

complaint_bp = Blueprint('complaint', __name__)

def generate_complaint_number():
    """Generate unique complaint number"""
    today = date.today()
    date_part = today.strftime('%y%m%d')
    random_part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    return f"CMP{date_part}{random_part}"

@complaint_bp.route('/', methods=['POST'])
@require_staff()
@validate_json_request('customer_id', 'title', 'description', 'category')
def create_complaint(current_user):
    """Create new complaint"""
    data = request.get_json()
    
    # Validate customer
    customer = Customer.query.get(data['customer_id'])
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    # Check branch access
    if not current_user.has_branch_access(customer.branch_id):
        return jsonify({'error': 'Access denied for customer branch'}), 403
    
    # Validate category
    valid_categories = ['service', 'cleanliness', 'equipment', 'staff', 'billing', 'other']
    if data['category'] not in valid_categories:
        return jsonify({'error': 'Invalid category', 'valid_categories': valid_categories}), 400
    
    # Validate priority if provided
    priority = data.get('priority', 'medium')
    valid_priorities = ['low', 'medium', 'high', 'critical']
    if priority not in valid_priorities:
        return jsonify({'error': 'Invalid priority', 'valid_priorities': valid_priorities}), 400
    
    # Generate complaint number
    complaint_number = generate_complaint_number()
    while Complaint.query.filter_by(complaint_number=complaint_number).first():
        complaint_number = generate_complaint_number()
    
    # Create complaint
    complaint = Complaint(
        complaint_number=complaint_number,
        title=data['title'],
        description=data['description'],
        category=data['category'],
        priority=priority,
        customer_id=data['customer_id'],
        branch_id=customer.branch_id
    )
    
    try:
        db.session.add(complaint)
        db.session.commit()
        
        return jsonify({
            'message': 'Complaint created successfully',
            'complaint': complaint.to_dict(include_customer=True)
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create complaint', 'details': str(e)}), 500

@complaint_bp.route('/', methods=['GET'])
@require_staff()
def list_complaints(current_user):
    """List complaints with filtering"""
    query = Complaint.query.join(Customer)
    
    # Branch-based filtering for non-owners
    if current_user.role != 'owner':
        query = query.filter(Complaint.branch_id == current_user.branch_id)
    
    # Apply filters
    branch_id = request.args.get('branch_id')
    if branch_id and current_user.has_branch_access(int(branch_id)):
        query = query.filter(Complaint.branch_id == int(branch_id))
    
    status = request.args.get('status')
    if status:
        query = query.filter(Complaint.status == status)
    
    category = request.args.get('category')
    if category:
        query = query.filter(Complaint.category == category)
    
    priority = request.args.get('priority')
    if priority:
        query = query.filter(Complaint.priority == priority)
    
    assigned_to = request.args.get('assigned_to')
    if assigned_to:
        query = query.filter(Complaint.assigned_to_id == int(assigned_to))
    
    # Date filters
    start_date = request.args.get('start_date')
    if start_date:
        query = query.filter(Complaint.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
    
    end_date = request.args.get('end_date')
    if end_date:
        query = query.filter(Complaint.created_at <= datetime.strptime(end_date, '%Y-%m-%d'))
    
    # Pagination
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    complaints_paginated = query.order_by(Complaint.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    complaints_data = []
    for complaint in complaints_paginated.items:
        complaint_dict = complaint.to_dict(include_customer=True)
        if complaint.assigned_to:
            complaint_dict['assigned_to'] = {
                'id': complaint.assigned_to.id,
                'name': f"{complaint.assigned_to.first_name} {complaint.assigned_to.last_name}",
                'role': complaint.assigned_to.role
            }
        complaints_data.append(complaint_dict)
    
    return jsonify({
        'complaints': complaints_data,
        'pagination': {
            'page': page,
            'pages': complaints_paginated.pages,
            'per_page': per_page,
            'total': complaints_paginated.total
        }
    }), 200

@complaint_bp.route('/<int:complaint_id>', methods=['GET'])
@require_staff()
def get_complaint(complaint_id, current_user):
    """Get complaint details"""
    complaint = Complaint.query.get_or_404(complaint_id)
    
    # Check branch access
    if not current_user.has_branch_access(complaint.branch_id):
        return jsonify({'error': 'Access denied for this complaint'}), 403
    
    complaint_data = complaint.to_dict(include_updates=True, include_customer=True)
    
    # Add assignment information
    if complaint.assigned_to:
        complaint_data['assigned_to'] = {
            'id': complaint.assigned_to.id,
            'name': f"{complaint.assigned_to.first_name} {complaint.assigned_to.last_name}",
            'role': complaint.assigned_to.role,
            'email': complaint.assigned_to.email
        }
    
    if complaint.resolved_by:
        complaint_data['resolved_by'] = {
            'id': complaint.resolved_by.id,
            'name': f"{complaint.resolved_by.first_name} {complaint.resolved_by.last_name}",
            'role': complaint.resolved_by.role
        }
    
    return jsonify(complaint_data), 200

@complaint_bp.route('/<int:complaint_id>/assign', methods=['POST'])
@require_manager_or_owner()
@validate_json_request('assigned_to_id')
def assign_complaint(complaint_id, current_user):
    """Assign complaint to staff member"""
    complaint = Complaint.query.get_or_404(complaint_id)
    data = request.get_json()
    
    # Check branch access
    if not current_user.has_branch_access(complaint.branch_id):
        return jsonify({'error': 'Access denied for this complaint'}), 403
    
    # Validate assigned user
    assigned_user = User.query.get(data['assigned_to_id'])
    if not assigned_user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if assigned user has access to this branch
    if not assigned_user.has_branch_access(complaint.branch_id) and assigned_user.role != 'owner':
        return jsonify({'error': 'User does not have access to this branch'}), 400
    
    success, message = complaint.assign_to_user(data['assigned_to_id'])
    
    if success:
        # Add update
        update = complaint.add_update(
            f"Complaint assigned to {assigned_user.first_name} {assigned_user.last_name}",
            current_user.id
        )
        
        db.session.commit()
        
        return jsonify({
            'message': message,
            'complaint': complaint.to_dict(include_customer=True)
        }), 200
    else:
        return jsonify({'error': message}), 400

@complaint_bp.route('/<int:complaint_id>/update', methods=['POST'])
@require_staff()
@validate_json_request('update_text')
def add_complaint_update(complaint_id, current_user):
    """Add update/comment to complaint"""
    complaint = Complaint.query.get_or_404(complaint_id)
    data = request.get_json()
    
    # Check branch access
    if not current_user.has_branch_access(complaint.branch_id):
        return jsonify({'error': 'Access denied for this complaint'}), 403
    
    # Check if user is assigned to complaint or has management role
    if (current_user.role not in ['owner', 'branch_manager'] and 
        complaint.assigned_to_id != current_user.id):
        return jsonify({'error': 'Only assigned staff or managers can add updates'}), 403
    
    try:
        update = complaint.add_update(data['update_text'], current_user.id)
        db.session.commit()
        
        return jsonify({
            'message': 'Update added successfully',
            'update': update.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add update', 'details': str(e)}), 500

@complaint_bp.route('/<int:complaint_id>/resolve', methods=['POST'])
@require_staff()
@validate_json_request('resolution_notes')
def resolve_complaint(complaint_id, current_user):
    """Mark complaint as resolved"""
    complaint = Complaint.query.get_or_404(complaint_id)
    data = request.get_json()
    
    # Check branch access
    if not current_user.has_branch_access(complaint.branch_id):
        return jsonify({'error': 'Access denied for this complaint'}), 403
    
    # Check if user is assigned to complaint or has management role
    if (current_user.role not in ['owner', 'branch_manager'] and 
        complaint.assigned_to_id != current_user.id):
        return jsonify({'error': 'Only assigned staff or managers can resolve complaints'}), 403
    
    success, message = complaint.resolve_complaint(
        data['resolution_notes'], 
        current_user.id
    )
    
    if success:
        # Add resolution update
        update = complaint.add_update(
            f"Complaint resolved: {data['resolution_notes']}",
            current_user.id
        )
        
        db.session.commit()
        
        return jsonify({
            'message': message,
            'complaint': complaint.to_dict(include_customer=True)
        }), 200
    else:
        return jsonify({'error': message}), 400

@complaint_bp.route('/<int:complaint_id>/close', methods=['POST'])
@require_manager_or_owner()
def close_complaint(complaint_id, current_user):
    """Close resolved complaint with customer feedback"""
    complaint = Complaint.query.get_or_404(complaint_id)
    data = request.get_json() or {}
    
    # Check branch access
    if not current_user.has_branch_access(complaint.branch_id):
        return jsonify({'error': 'Access denied for this complaint'}), 403
    
    customer_rating = data.get('customer_rating')
    customer_feedback = data.get('customer_feedback')
    
    # Validate rating if provided
    if customer_rating is not None:
        try:
            customer_rating = int(customer_rating)
            if customer_rating < 1 or customer_rating > 5:
                return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid rating format'}), 400
    
    success, message = complaint.close_complaint(customer_rating, customer_feedback)
    
    if success:
        # Add closure update
        update_text = "Complaint closed"
        if customer_rating:
            update_text += f" with customer rating: {customer_rating}/5"
        if customer_feedback:
            update_text += f". Customer feedback: {customer_feedback}"
        
        update = complaint.add_update(update_text, current_user.id)
        db.session.commit()
        
        return jsonify({
            'message': message,
            'complaint': complaint.to_dict(include_customer=True)
        }), 200
    else:
        return jsonify({'error': message}), 400

@complaint_bp.route('/summary', methods=['GET'])
@require_staff()
def complaint_summary(current_user):
    """Get complaint summary statistics"""
    # Base query with branch filtering
    base_query = Complaint.query
    
    if current_user.role != 'owner':
        base_query = base_query.filter(Complaint.branch_id == current_user.branch_id)
    
    branch_id = request.args.get('branch_id')
    if branch_id and current_user.has_branch_access(int(branch_id)):
        base_query = base_query.filter(Complaint.branch_id == int(branch_id))
    
    # Status breakdown
    status_counts = {
        'open': base_query.filter_by(status='open').count(),
        'in_progress': base_query.filter_by(status='in_progress').count(),
        'resolved': base_query.filter_by(status='resolved').count(),
        'closed': base_query.filter_by(status='closed').count()
    }
    
    # Priority breakdown
    priority_counts = {
        'low': base_query.filter_by(priority='low').count(),
        'medium': base_query.filter_by(priority='medium').count(),
        'high': base_query.filter_by(priority='high').count(),
        'critical': base_query.filter_by(priority='critical').count()
    }
    
    # Category breakdown
    category_counts = {
        'service': base_query.filter_by(category='service').count(),
        'cleanliness': base_query.filter_by(category='cleanliness').count(),
        'equipment': base_query.filter_by(category='equipment').count(),
        'staff': base_query.filter_by(category='staff').count(),
        'billing': base_query.filter_by(category='billing').count(),
        'other': base_query.filter_by(category='other').count()
    }
    
    # Calculate average resolution time for closed complaints
    from sqlalchemy import func
    avg_resolution = db.session.query(
        func.avg(func.julianday(Complaint.resolved_date) - func.julianday(Complaint.created_at))
    ).filter(
        Complaint.status == 'closed',
        Complaint.resolved_date.isnot(None)
    )
    
    if current_user.role != 'owner':
        avg_resolution = avg_resolution.filter(Complaint.branch_id == current_user.branch_id)
    
    avg_resolution_days = avg_resolution.scalar() or 0
    
    # Customer satisfaction (average rating)
    avg_satisfaction = db.session.query(
        func.avg(Complaint.customer_rating)
    ).filter(
        Complaint.status == 'closed',
        Complaint.customer_rating.isnot(None)
    )
    
    if current_user.role != 'owner':
        avg_satisfaction = avg_satisfaction.filter(Complaint.branch_id == current_user.branch_id)
    
    avg_rating = avg_satisfaction.scalar() or 0
    
    return jsonify({
        'status_breakdown': status_counts,
        'priority_breakdown': priority_counts,
        'category_breakdown': category_counts,
        'metrics': {
            'total_complaints': sum(status_counts.values()),
            'avg_resolution_days': round(avg_resolution_days, 1),
            'avg_customer_rating': round(float(avg_rating), 1) if avg_rating else None,
            'urgent_complaints': priority_counts['high'] + priority_counts['critical']
        }
    }), 200
