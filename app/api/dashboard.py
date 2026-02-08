"""Dashboard API routes for analytics and reporting"""
from flask import Blueprint, request, jsonify
from datetime import date, datetime, timedelta
from sqlalchemy import func, and_, or_
from app.database import db
from app.models.user import User
from app.models.customer import Customer
from app.models.subscription import Subscription, SubscriptionPlan
from app.models.payment import Payment
from app.models.attendance import Attendance
from app.models.complaint import Complaint
from app.models.branch import Branch
from app.auth import require_staff, require_owner, require_manager_or_owner

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/owner', methods=['GET'])
@require_owner()
def owner_dashboard(current_user):
    """Owner dashboard with system-wide analytics"""
    # Date range (default current month)
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
    
    # Revenue Summary
    revenue_query = Payment.query.filter(
        Payment.status == 'completed',
        Payment.payment_date >= start_date,
        Payment.payment_date <= end_date
    )
    
    total_revenue = db.session.query(func.sum(Payment.amount)).filter(
        Payment.status == 'completed',
        Payment.payment_date >= start_date,
        Payment.payment_date <= end_date
    ).scalar() or 0
    
    # Revenue by branch
    revenue_by_branch = db.session.query(
        Branch.name,
        Branch.code,
        func.sum(Payment.amount).label('revenue'),
        func.count(Payment.id).label('payments')
    ).join(Payment).filter(
        Payment.status == 'completed',
        Payment.payment_date >= start_date,
        Payment.payment_date <= end_date
    ).group_by(Branch.id).all()
    
    # Active Subscriptions by Branch
    active_subs_by_branch = db.session.query(
        Branch.name,
        Branch.code,
        func.count(Subscription.id).label('active_subscriptions')
    ).join(Subscription).filter(
        Subscription.status == 'active'
    ).group_by(Branch.id).all()
    
    # New Customers This Month
    new_customers = Customer.query.filter(
        Customer.joined_date >= start_date,
        Customer.joined_date <= end_date
    ).count()
    
    # Expiring Subscriptions (next 7 days)
    expiring_soon = Subscription.query.filter(
        Subscription.status == 'active',
        Subscription.end_date >= today,
        Subscription.end_date <= today + timedelta(days=7)
    ).count()
    
    # Attendance Statistics
    total_attendance = Attendance.query.filter(
        Attendance.entry_date >= start_date,
        Attendance.entry_date <= end_date,
        Attendance.access_granted == True
    ).count()
    
    # Open Complaints
    open_complaints = Complaint.query.filter(
        Complaint.status.in_(['open', 'in_progress'])
    ).count()
    
    # Critical Alerts
    alerts = []
    
    # High priority open complaints
    critical_complaints = Complaint.query.filter(
        Complaint.status.in_(['open', 'in_progress']),
        Complaint.priority == 'critical'
    ).count()
    if critical_complaints > 0:
        alerts.append({
            'type': 'critical',
            'message': f"{critical_complaints} critical complaints need attention",
            'count': critical_complaints
        })
    
    # Subscriptions expiring today
    expiring_today = Subscription.query.filter(
        Subscription.status == 'active',
        Subscription.end_date == today
    ).count()
    if expiring_today > 0:
        alerts.append({
            'type': 'warning',
            'message': f"{expiring_today} subscriptions expire today",
            'count': expiring_today
        })
    
    # Pending payments
    pending_payments = Payment.query.filter(
        Payment.status == 'pending',
        Payment.payment_date >= today - timedelta(days=7)
    ).count()
    if pending_payments > 0:
        alerts.append({
            'type': 'info',
            'message': f"{pending_payments} payments pending processing",
            'count': pending_payments
        })
    
    return jsonify({
        'period': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        },
        'summary': {
            'total_revenue': float(total_revenue),
            'new_customers': new_customers,
            'active_subscriptions': Subscription.query.filter_by(status='active').count(),
            'total_attendance': total_attendance,
            'expiring_subscriptions': expiring_soon,
            'open_complaints': open_complaints
        },
        'revenue_by_branch': [{
            'branch_name': row.name,
            'branch_code': row.code,
            'revenue': float(row.revenue),
            'payments': row.payments
        } for row in revenue_by_branch],
        'subscriptions_by_branch': [{
            'branch_name': row.name,
            'branch_code': row.code,
            'active_subscriptions': row.active_subscriptions
        } for row in active_subs_by_branch],
        'alerts': alerts
    }), 200

@dashboard_bp.route('/branch/<int:branch_id>', methods=['GET'])
@require_manager_or_owner()
def branch_dashboard(branch_id, current_user):
    """Branch-specific dashboard"""
    # Check branch access
    if not current_user.has_branch_access(branch_id):
        return jsonify({'error': 'Access denied for this branch'}), 403
    
    branch = Branch.query.get_or_404(branch_id)
    
    # Date range (default current month)
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
    
    # Branch Revenue
    branch_revenue = db.session.query(func.sum(Payment.amount)).filter(
        Payment.branch_id == branch_id,
        Payment.status == 'completed',
        Payment.payment_date >= start_date,
        Payment.payment_date <= end_date
    ).scalar() or 0
    
    # Monthly Target Progress
    target_progress = 0
    if branch.monthly_target:
        target_progress = (float(branch_revenue) / float(branch.monthly_target)) * 100
    
    # Customer Statistics
    total_customers = Customer.query.filter_by(branch_id=branch_id, is_active=True).count()
    new_customers_period = Customer.query.filter(
        Customer.branch_id == branch_id,
        Customer.joined_date >= start_date,
        Customer.joined_date <= end_date
    ).count()
    
    # Subscription Statistics
    active_subscriptions = Subscription.query.filter(
        Subscription.branch_id == branch_id,
        Subscription.status == 'active'
    ).count()
    
    expiring_subscriptions = Subscription.query.filter(
        Subscription.branch_id == branch_id,
        Subscription.status == 'active',
        Subscription.end_date >= today,
        Subscription.end_date <= today + timedelta(days=7)
    ).count()
    
    # Popular subscription plans
    popular_plans = db.session.query(
        SubscriptionPlan.name,
        func.count(Subscription.id).label('count')
    ).join(Subscription).filter(
        Subscription.branch_id == branch_id,
        Subscription.status.in_(['active', 'pending']),
        Subscription.created_at >= start_date
    ).group_by(SubscriptionPlan.id).order_by(func.count(Subscription.id).desc()).limit(5).all()
    
    # Attendance Statistics
    today_attendance = Attendance.query.filter(
        Attendance.branch_id == branch_id,
        Attendance.entry_date == today,
        Attendance.access_granted == True
    ).count()
    
    period_attendance = Attendance.query.filter(
        Attendance.branch_id == branch_id,
        Attendance.entry_date >= start_date,
        Attendance.entry_date <= end_date,
        Attendance.access_granted == True
    ).count()
    
    # Payment Method Breakdown
    payment_methods = db.session.query(
        Payment.payment_method,
        func.count(Payment.id).label('count'),
        func.sum(Payment.amount).label('amount')
    ).filter(
        Payment.branch_id == branch_id,
        Payment.status == 'completed',
        Payment.payment_date >= start_date,
        Payment.payment_date <= end_date
    ).group_by(Payment.payment_method).all()
    
    # Branch Complaints
    open_complaints = Complaint.query.filter(
        Complaint.branch_id == branch_id,
        Complaint.status.in_(['open', 'in_progress'])
    ).count()
    
    return jsonify({
        'branch': branch.to_dict(),
        'period': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        },
        'financial': {
            'revenue': float(branch_revenue),
            'monthly_target': float(branch.monthly_target) if branch.monthly_target else 0,
            'target_progress_percent': round(target_progress, 1)
        },
        'customers': {
            'total_active': total_customers,
            'new_this_period': new_customers_period
        },
        'subscriptions': {
            'active': active_subscriptions,
            'expiring_soon': expiring_subscriptions
        },
        'attendance': {
            'today': today_attendance,
            'period_total': period_attendance
        },
        'popular_plans': [{
            'plan_name': row.name,
            'subscription_count': row.count
        } for row in popular_plans],
        'payment_methods': [{
            'method': row.payment_method,
            'count': row.count,
            'amount': float(row.amount)
        } for row in payment_methods],
        'complaints': {
            'open': open_complaints
        }
    }), 200

@dashboard_bp.route('/accountant', methods=['GET'])
@require_staff()
def accountant_dashboard(current_user):
    """Accountant dashboard for financial overview"""
    if current_user.role not in ['owner', 'branch_manager', 'accountant']:
        return jsonify({'error': 'Access denied'}), 403
    
    # Date range (default current month)
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
    
    # Base query for branch filtering
    payment_query = Payment.query.filter(
        Payment.payment_date >= start_date,
        Payment.payment_date <= end_date
    )
    
    # Branch filtering for non-owners
    if current_user.role != 'owner':
        payment_query = payment_query.filter(Payment.branch_id == current_user.branch_id)
    
    # Financial Summary
    completed_payments = payment_query.filter(Payment.status == 'completed')
    total_revenue = db.session.query(func.sum(Payment.amount)).filter(
        Payment.id.in_(p.id for p in completed_payments)
    ).scalar() or 0
    
    pending_amount = db.session.query(func.sum(Payment.amount)).filter(
        Payment.status == 'pending',
        Payment.payment_date >= start_date,
        Payment.payment_date <= end_date
    ).scalar() or 0
    
    refunded_amount = db.session.query(func.sum(Payment.amount)).filter(
        Payment.status == 'refunded',
        Payment.payment_date >= start_date,
        Payment.payment_date <= end_date
    ).scalar() or 0
    
    # Daily revenue breakdown
    daily_revenue = db.session.query(
        Payment.payment_date,
        func.sum(Payment.amount).label('daily_total')
    ).filter(
        Payment.status == 'completed',
        Payment.payment_date >= start_date,
        Payment.payment_date <= end_date
    )
    
    if current_user.role != 'owner':
        daily_revenue = daily_revenue.filter(Payment.branch_id == current_user.branch_id)
    
    daily_revenue = daily_revenue.group_by(Payment.payment_date).order_by(Payment.payment_date).all()
    
    # Cash reconciliation data
    cash_payments = payment_query.filter(
        Payment.payment_method == 'cash',
        Payment.status == 'completed'
    ).all()
    
    cash_total = sum(float(p.amount) for p in cash_payments)
    
    return jsonify({
        'period': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        },
        'financial_summary': {
            'total_revenue': float(total_revenue),
            'pending_amount': float(pending_amount or 0),
            'refunded_amount': float(refunded_amount or 0),
            'net_revenue': float(total_revenue) - float(refunded_amount or 0)
        },
        'cash_reconciliation': {
            'cash_payments_count': len(cash_payments),
            'cash_total': cash_total
        },
        'daily_revenue': [{
            'date': row.payment_date.isoformat(),
            'amount': float(row.daily_total)
        } for row in daily_revenue]
    }), 200

@dashboard_bp.route('/manager', methods=['GET'])
@require_manager_or_owner()
def manager_dashboard(current_user):
    """Branch manager dashboard - shows their branch data"""
    if not current_user.branch_id:
        return jsonify({'error': 'No branch assigned to this manager'}), 400

    # Get manager's branch
    branch_id = current_user.branch_id
    branch = Branch.query.get_or_404(branch_id)

    # Date range (default current month)
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

    # Branch Revenue
    branch_revenue = db.session.query(func.sum(Payment.amount)).filter(
        Payment.branch_id == branch_id,
        Payment.status == 'completed',
        Payment.payment_date >= start_date,
        Payment.payment_date <= end_date
    ).scalar() or 0

    # Monthly Target Progress
    target_progress = 0
    if branch.monthly_target:
        target_progress = (float(branch_revenue) / float(branch.monthly_target)) * 100

    # Customer Statistics
    total_customers = Customer.query.filter_by(branch_id=branch_id).filter(
        Customer.user.has(is_active=True)
    ).count()
    new_customers_period = Customer.query.filter(
        Customer.branch_id == branch_id,
        Customer.joined_date >= start_date,
        Customer.joined_date <= end_date
    ).count()

    # Subscription Statistics
    active_subscriptions = Subscription.query.filter(
        Subscription.branch_id == branch_id,
        Subscription.status == 'active'
    ).count()

    expiring_subscriptions = Subscription.query.filter(
        Subscription.branch_id == branch_id,
        Subscription.status == 'active',
        Subscription.end_date >= today,
        Subscription.end_date <= today + timedelta(days=7)
    ).count()

    # Popular subscription plans
    popular_plans = db.session.query(
        SubscriptionPlan.name,
        func.count(Subscription.id).label('count')
    ).join(Subscription).filter(
        Subscription.branch_id == branch_id,
        Subscription.status.in_(['active', 'pending']),
        Subscription.created_at >= start_date
    ).group_by(SubscriptionPlan.id).order_by(func.count(Subscription.id).desc()).limit(5).all()

    # Attendance Statistics
    today_attendance = Attendance.query.filter(
        Attendance.branch_id == branch_id,
        Attendance.entry_date == today,
        Attendance.access_granted == True
    ).count()

    period_attendance = Attendance.query.filter(
        Attendance.branch_id == branch_id,
        Attendance.entry_date >= start_date,
        Attendance.entry_date <= end_date,
        Attendance.access_granted == True
    ).count()

    # Payment Method Breakdown
    payment_methods = db.session.query(
        Payment.payment_method,
        func.count(Payment.id).label('count'),
        func.sum(Payment.amount).label('amount')
    ).filter(
        Payment.branch_id == branch_id,
        Payment.status == 'completed',
        Payment.payment_date >= start_date,
        Payment.payment_date <= end_date
    ).group_by(Payment.payment_method).all()

    # Branch Complaints
    open_complaints = Complaint.query.filter(
        Complaint.branch_id == branch_id,
        Complaint.status.in_(['open', 'in_progress'])
    ).count()

    return jsonify({
        'branch': branch.to_dict(),
        'period': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        },
        'financial': {
            'revenue': float(branch_revenue),
            'monthly_target': float(branch.monthly_target) if branch.monthly_target else 0,
            'target_progress_percent': round(target_progress, 1)
        },
        'customers': {
            'total_active': total_customers,
            'new_this_period': new_customers_period
        },
        'subscriptions': {
            'active': active_subscriptions,
            'expiring_soon': expiring_subscriptions
        },
        'attendance': {
            'today': today_attendance,
            'period_total': period_attendance
        },
        'popular_plans': [{
            'plan_name': row.name,
            'subscription_count': row.count
        } for row in popular_plans],
        'payment_methods': [{
            'method': row.payment_method,
            'count': row.count,
            'amount': float(row.amount)
        } for row in payment_methods],
        'complaints': {
            'open': open_complaints
        }
    }), 200

@dashboard_bp.route('/staff', methods=['GET'])
@require_staff()
def staff_dashboard(current_user):
    """Staff dashboard for receptionists and accountants"""
    if not current_user.branch_id:
        return jsonify({'error': 'No branch assigned to this user'}), 400

    # Date range (default today)
    today = date.today()
    start_date = request.args.get('start_date')
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date = today

    end_date = request.args.get('end_date')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        end_date = today

    branch_id = current_user.branch_id

    # Today's attendance
    today_attendance = Attendance.query.filter(
        Attendance.branch_id == branch_id,
        Attendance.entry_date == today,
        Attendance.access_granted == True
    ).count()

    # Active customers
    active_customers = Customer.query.filter(
        Customer.branch_id == branch_id,
        Customer.is_active == True
    ).count()

    # Active subscriptions
    active_subscriptions = Subscription.query.filter(
        Subscription.branch_id == branch_id,
        Subscription.status == 'active'
    ).count()

    # Today's revenue (for accountants)
    today_revenue = 0
    if current_user.role in ['accountant', 'branch_manager']:
        today_revenue = db.session.query(func.sum(Payment.amount)).filter(
            Payment.branch_id == branch_id,
            Payment.status == 'completed',
            Payment.payment_date == today
        ).scalar() or 0

    # Pending tasks
    pending_complaints = Complaint.query.filter(
        Complaint.branch_id == branch_id,
        Complaint.status == 'open'
    ).count()

    # New customers today
    new_customers = Customer.query.filter(
        Customer.branch_id == branch_id,
        Customer.joined_date == today
    ).count()

    return jsonify({
        'period': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        },
        'summary': {
            'total_attendance': today_attendance,
            'active_subscriptions': active_subscriptions,
            'new_customers': new_customers,
            'total_revenue': float(today_revenue)
        },
        'branch_id': branch_id
    }), 200

@dashboard_bp.route('/alerts', methods=['GET'])
@require_staff()
def get_alerts(current_user):
    """Get system alerts and notifications"""
    alerts = []
    today = date.today()
    
    # Branch filtering for non-owners
    branch_filter = {}
    if current_user.role != 'owner':
        branch_filter['branch_id'] = current_user.branch_id
    
    # Expiring subscriptions
    expiring_subscriptions = Subscription.query.filter(
        Subscription.status == 'active',
        Subscription.end_date >= today,
        Subscription.end_date <= today + timedelta(days=3)
    )
    
    if current_user.role != 'owner':
        expiring_subscriptions = expiring_subscriptions.filter(
            Subscription.branch_id == current_user.branch_id
        )
    
    expiring_count = expiring_subscriptions.count()
    if expiring_count > 0:
        alerts.append({
            'type': 'warning',
            'category': 'subscriptions',
            'title': 'Subscriptions Expiring Soon',
            'message': f"{expiring_count} subscriptions expire in the next 3 days",
            'count': expiring_count,
            'priority': 'medium'
        })
    
    # Pending payments older than 2 days
    old_pending_payments = Payment.query.filter(
        Payment.status == 'pending',
        Payment.created_at <= datetime.utcnow() - timedelta(days=2)
    )
    
    if current_user.role != 'owner':
        old_pending_payments = old_pending_payments.filter(
            Payment.branch_id == current_user.branch_id
        )
    
    pending_count = old_pending_payments.count()
    if pending_count > 0:
        alerts.append({
            'type': 'warning',
            'category': 'payments',
            'title': 'Pending Payments',
            'message': f"{pending_count} payments have been pending for 2+ days",
            'count': pending_count,
            'priority': 'medium'
        })
    
    # High priority complaints
    high_priority_complaints = Complaint.query.filter(
        Complaint.status.in_(['open', 'in_progress']),
        Complaint.priority.in_(['high', 'critical'])
    )
    
    if current_user.role != 'owner':
        high_priority_complaints = high_priority_complaints.filter(
            Complaint.branch_id == current_user.branch_id
        )
    
    complaint_count = high_priority_complaints.count()
    if complaint_count > 0:
        alerts.append({
            'type': 'error',
            'category': 'complaints',
            'title': 'High Priority Complaints',
            'message': f"{complaint_count} high/critical priority complaints need attention",
            'count': complaint_count,
            'priority': 'high'
        })
    
    return jsonify({
        'alerts': alerts,
        'total': len(alerts),
        'generated_at': datetime.utcnow().isoformat()
    }), 200
