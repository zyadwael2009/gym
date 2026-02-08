"""Branch management API routes"""
from flask import Blueprint, request, jsonify
from app.database import db
from app.models.branch import Branch
from app.models.user import User
from app.auth import require_owner, require_manager_or_owner, require_staff, validate_json_request

branch_bp = Blueprint('branch', __name__)

@branch_bp.route('/', methods=['GET'])
@require_staff()
def list_branches(current_user):
    """List branches (filtered by user access)"""
    query = Branch.query
    
    # Branch managers can only see their own branch
    if current_user.role == 'branch_manager':
        query = query.filter_by(id=current_user.branch_id)
    elif current_user.role in ['receptionist', 'accountant']:
        query = query.filter_by(id=current_user.branch_id)
    
    # Apply filters
    is_active = request.args.get('is_active')
    if is_active is not None:
        query = query.filter_by(is_active=is_active.lower() == 'true')
    
    branches = query.all()
    
    return jsonify({
        'branches': [branch.to_dict() for branch in branches],
        'total': len(branches)
    }), 200

@branch_bp.route('/', methods=['POST'])
@require_owner()
@validate_json_request('name', 'code')
def create_branch(current_user):
    """Create new branch (owner only)"""
    data = request.get_json()
    
    # Check if branch code already exists
    if Branch.query.filter_by(code=data['code']).first():
        return jsonify({'error': 'Branch code already exists'}), 400
    
    branch = Branch(
        name=data['name'],
        code=data['code'],
        address_line1=data.get('address_line1'),
        address_line2=data.get('address_line2'),
        city=data.get('city'),
        state=data.get('state'),
        pincode=data.get('pincode'),
        country=data.get('country', 'India'),
        phone=data.get('phone'),
        email=data.get('email'),
        monthly_target=data.get('monthly_target', 0)
    )
    
    # Handle opening and closing times
    if data.get('opening_time'):
        from datetime import time
        try:
            hour, minute = map(int, data['opening_time'].split(':'))
            branch.opening_time = time(hour, minute)
        except ValueError:
            return jsonify({'error': 'Invalid opening_time format. Use HH:MM'}), 400
    
    if data.get('closing_time'):
        from datetime import time
        try:
            hour, minute = map(int, data['closing_time'].split(':'))
            branch.closing_time = time(hour, minute)
        except ValueError:
            return jsonify({'error': 'Invalid closing_time format. Use HH:MM'}), 400
    
    try:
        db.session.add(branch)
        db.session.commit()
        
        return jsonify({
            'message': 'Branch created successfully',
            'branch': branch.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create branch', 'details': str(e)}), 500

@branch_bp.route('/<int:branch_id>', methods=['GET'])
@require_staff()
def get_branch(branch_id, current_user):
    """Get branch details"""
    branch = Branch.query.get_or_404(branch_id)
    
    # Check access permissions
    if not current_user.has_branch_access(branch_id):
        return jsonify({'error': 'Access denied for this branch'}), 403
    
    branch_data = branch.to_dict()
    
    # Add manager information
    if branch.manager:
        branch_data['manager'] = {
            'id': branch.manager.id,
            'name': f"{branch.manager.first_name} {branch.manager.last_name}",
            'email': branch.manager.email,
            'phone': branch.manager.phone
        }
    
    return jsonify(branch_data), 200

@branch_bp.route('/<int:branch_id>', methods=['PUT'])
@require_manager_or_owner()
def update_branch(branch_id, current_user):
    """Update branch details"""
    branch = Branch.query.get_or_404(branch_id)
    
    # Check access permissions
    if not current_user.has_branch_access(branch_id):
        return jsonify({'error': 'Access denied for this branch'}), 403
    
    data = request.get_json()
    
    # Update allowed fields
    updatable_fields = [
        'name', 'address_line1', 'address_line2', 'city', 'state', 
        'pincode', 'country', 'phone', 'email', 'monthly_target'
    ]
    
    # Only owner can update code and manager
    if current_user.role == 'owner':
        updatable_fields.extend(['code', 'manager_id', 'is_active'])
    
    for field in updatable_fields:
        if field in data and data[field] is not None:
            # Special validation for code changes
            if field == 'code' and data[field] != branch.code:
                if Branch.query.filter_by(code=data[field]).first():
                    return jsonify({'error': 'Branch code already exists'}), 400
            
            # Special validation for manager assignment
            if field == 'manager_id':
                manager = User.query.get(data[field])
                if not manager or manager.role != 'branch_manager':
                    return jsonify({'error': 'Invalid manager ID'}), 400
            
            setattr(branch, field, data[field])
    
    # Handle time fields
    if 'opening_time' in data:
        from datetime import time
        try:
            hour, minute = map(int, data['opening_time'].split(':'))
            branch.opening_time = time(hour, minute)
        except ValueError:
            return jsonify({'error': 'Invalid opening_time format. Use HH:MM'}), 400
    
    if 'closing_time' in data:
        from datetime import time
        try:
            hour, minute = map(int, data['closing_time'].split(':'))
            branch.closing_time = time(hour, minute)
        except ValueError:
            return jsonify({'error': 'Invalid closing_time format. Use HH:MM'}), 400
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Branch updated successfully',
            'branch': branch.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update branch', 'details': str(e)}), 500

@branch_bp.route('/<int:branch_id>', methods=['DELETE'])
@require_owner()
def delete_branch(branch_id, current_user):
    """Delete branch (owner only)"""
    branch = Branch.query.get_or_404(branch_id)
    
    # Check if branch has active customers/subscriptions
    from app.models.customer import Customer
    active_customers = Customer.query.filter_by(branch_id=branch_id, is_active=True).count()
    
    if active_customers > 0:
        return jsonify({
            'error': 'Cannot delete branch with active customers',
            'active_customers': active_customers
        }), 400
    
    try:
        # Soft delete by marking as inactive
        branch.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Branch deactivated successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to deactivate branch', 'details': str(e)}), 500

@branch_bp.route('/<int:branch_id>/assign-manager', methods=['POST'])
@require_owner()
@validate_json_request('manager_id')
def assign_manager(branch_id, current_user):
    """Assign manager to branch"""
    branch = Branch.query.get_or_404(branch_id)
    data = request.get_json()
    
    manager = User.query.get(data['manager_id'])
    if not manager:
        return jsonify({'error': 'Manager not found'}), 404
    
    if manager.role != 'branch_manager':
        return jsonify({'error': 'User must have branch_manager role'}), 400
    
    # Check if manager is already assigned to another branch
    if manager.branch_id and manager.branch_id != branch_id:
        return jsonify({'error': 'Manager already assigned to another branch'}), 400
    
    try:
        # Update both branch and manager
        branch.manager_id = manager.id
        manager.branch_id = branch_id
        
        db.session.commit()
        
        return jsonify({
            'message': 'Manager assigned successfully',
            'branch': branch.to_dict(),
            'manager': manager.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to assign manager', 'details': str(e)}), 500

@branch_bp.route('/<int:branch_id>/staff', methods=['GET'])
@require_manager_or_owner()
def get_branch_staff(branch_id, current_user):
    """Get all staff members for a branch"""
    # Check access permissions
    if not current_user.has_branch_access(branch_id):
        return jsonify({'error': 'Access denied for this branch'}), 403
    
    staff = User.query.filter_by(
        branch_id=branch_id,
        is_active=True
    ).filter(
        User.role.in_(['branch_manager', 'receptionist', 'accountant'])
    ).all()
    
    return jsonify({
        'staff': [user.to_dict() for user in staff],
        'total': len(staff)
    }), 200
