"""Notification service for alerts and reminders"""
from datetime import date, timedelta
from app.models.subscription import Subscription
from app.models.payment import Payment
from app.models.complaint import Complaint
from app.models.customer import Customer

class NotificationService:
    """Service for generating notifications and alerts"""
    
    @staticmethod
    def get_subscription_alerts(branch_id=None):
        """Get subscription-related alerts"""
        alerts = []
        today = date.today()
        
        # Base query
        query = Subscription.query
        if branch_id:
            query = query.filter(Subscription.branch_id == branch_id)
        
        # Expiring subscriptions
        expiring_soon = query.filter(
            Subscription.status == 'active',
            Subscription.end_date >= today,
            Subscription.end_date <= today + timedelta(days=7)
        ).count()
        
        if expiring_soon > 0:
            alerts.append({
                'type': 'subscription_expiring',
                'priority': 'medium',
                'count': expiring_soon,
                'message': f"{expiring_soon} subscriptions expiring in next 7 days",
                'action_required': 'Contact customers for renewal'
            })
        
        # Expired subscriptions that haven't been updated
        expired_today = query.filter(
            Subscription.status == 'active',
            Subscription.end_date == today
        ).count()
        
        if expired_today > 0:
            alerts.append({
                'type': 'subscription_expired',
                'priority': 'high',
                'count': expired_today,
                'message': f"{expired_today} subscriptions expired today",
                'action_required': 'Update subscription status'
            })
        
        # Long-term frozen subscriptions
        long_frozen = query.filter(
            Subscription.status == 'frozen',
            Subscription.current_freeze_start <= today - timedelta(days=20)
        ).count()
        
        if long_frozen > 0:
            alerts.append({
                'type': 'long_term_frozen',
                'priority': 'low',
                'count': long_frozen,
                'message': f"{long_frozen} subscriptions frozen for 20+ days",
                'action_required': 'Follow up with customers'
            })
        
        return alerts
    
    @staticmethod
    def get_payment_alerts(branch_id=None):
        """Get payment-related alerts"""
        alerts = []
        today = date.today()
        
        # Base query
        query = Payment.query
        if branch_id:
            query = query.filter(Payment.branch_id == branch_id)
        
        # Pending payments older than 24 hours
        old_pending = query.filter(
            Payment.status == 'pending',
            Payment.created_at <= today - timedelta(days=1)
        ).count()
        
        if old_pending > 0:
            alerts.append({
                'type': 'pending_payments',
                'priority': 'medium',
                'count': old_pending,
                'message': f"{old_pending} payments pending for 24+ hours",
                'action_required': 'Process or investigate pending payments'
            })
        
        # Failed payments in last 7 days
        recent_failed = query.filter(
            Payment.status == 'failed',
            Payment.created_at >= today - timedelta(days=7)
        ).count()
        
        if recent_failed > 0:
            alerts.append({
                'type': 'failed_payments',
                'priority': 'medium',
                'count': recent_failed,
                'message': f"{recent_failed} payments failed in last 7 days",
                'action_required': 'Contact customers for payment retry'
            })
        
        return alerts
    
    @staticmethod
    def get_complaint_alerts(branch_id=None):
        """Get complaint-related alerts"""
        alerts = []
        
        # Base query
        query = Complaint.query
        if branch_id:
            query = query.filter(Complaint.branch_id == branch_id)
        
        # Critical priority complaints
        critical_complaints = query.filter(
            Complaint.status.in_(['open', 'in_progress']),
            Complaint.priority == 'critical'
        ).count()
        
        if critical_complaints > 0:
            alerts.append({
                'type': 'critical_complaints',
                'priority': 'critical',
                'count': critical_complaints,
                'message': f"{critical_complaints} critical complaints need immediate attention",
                'action_required': 'Assign and resolve immediately'
            })
        
        # Old unassigned complaints
        old_unassigned = query.filter(
            Complaint.status == 'open',
            Complaint.assigned_to_id.is_(None),
            Complaint.created_at <= date.today() - timedelta(days=2)
        ).count()
        
        if old_unassigned > 0:
            alerts.append({
                'type': 'unassigned_complaints',
                'priority': 'medium',
                'count': old_unassigned,
                'message': f"{old_unassigned} complaints unassigned for 2+ days",
                'action_required': 'Assign to appropriate staff'
            })
        
        # Long-pending resolution
        long_pending = query.filter(
            Complaint.status == 'in_progress',
            Complaint.assigned_date <= date.today() - timedelta(days=7)
        ).count()
        
        if long_pending > 0:
            alerts.append({
                'type': 'long_pending_complaints',
                'priority': 'low',
                'count': long_pending,
                'message': f"{long_pending} complaints in progress for 7+ days",
                'action_required': 'Follow up on resolution progress'
            })
        
        return alerts
    
    @staticmethod
    def get_customer_alerts(branch_id=None):
        """Get customer-related alerts"""
        alerts = []
        today = date.today()
        
        # Base query for customers
        customer_query = Customer.query
        if branch_id:
            customer_query = customer_query.filter(Customer.branch_id == branch_id)
        
        # Customers without active subscriptions
        inactive_customers = customer_query.filter(
            Customer.is_active == True,
            ~Customer.subscriptions.any(
                Subscription.status == 'active'
            )
        ).count()
        
        if inactive_customers > 0:
            alerts.append({
                'type': 'customers_without_subscription',
                'priority': 'low',
                'count': inactive_customers,
                'message': f"{inactive_customers} active customers without subscriptions",
                'action_required': 'Follow up for new subscriptions'
            })
        
        # Customers with incomplete profiles
        incomplete_profiles = customer_query.filter(
            Customer.is_active == True,
            (Customer.height_cm.is_(None)) | (Customer.weight_kg.is_(None))
        ).count()
        
        if incomplete_profiles > 0:
            alerts.append({
                'type': 'incomplete_customer_profiles',
                'priority': 'low',
                'count': incomplete_profiles,
                'message': f"{incomplete_profiles} customers with incomplete health data",
                'action_required': 'Complete customer health assessments'
            })
        
        return alerts
    
    @staticmethod
    def get_all_alerts(branch_id=None):
        """Get all alerts for dashboard"""
        all_alerts = []
        
        # Collect all types of alerts
        all_alerts.extend(NotificationService.get_subscription_alerts(branch_id))
        all_alerts.extend(NotificationService.get_payment_alerts(branch_id))
        all_alerts.extend(NotificationService.get_complaint_alerts(branch_id))
        all_alerts.extend(NotificationService.get_customer_alerts(branch_id))
        
        # Sort by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        all_alerts.sort(key=lambda x: priority_order.get(x['priority'], 4))
        
        return {
            'alerts': all_alerts,
            'total': len(all_alerts),
            'by_priority': {
                'critical': len([a for a in all_alerts if a['priority'] == 'critical']),
                'high': len([a for a in all_alerts if a['priority'] == 'high']),
                'medium': len([a for a in all_alerts if a['priority'] == 'medium']),
                'low': len([a for a in all_alerts if a['priority'] == 'low'])
            },
            'generated_at': date.today().isoformat()
        }
    
    @staticmethod
    def get_renewal_reminders(branch_id=None, days_ahead=30):
        """Get list of customers to contact for subscription renewal"""
        cutoff_date = date.today() + timedelta(days=days_ahead)
        
        query = Subscription.query.filter(
            Subscription.status == 'active',
            Subscription.end_date <= cutoff_date,
            Subscription.end_date >= date.today()
        )
        
        if branch_id:
            query = query.filter(Subscription.branch_id == branch_id)
        
        expiring_subscriptions = query.order_by(Subscription.end_date.asc()).all()
        
        reminders = []
        for subscription in expiring_subscriptions:
            days_remaining = (subscription.end_date - date.today()).days
            
            reminders.append({
                'customer': {
                    'id': subscription.customer.id,
                    'member_id': subscription.customer.member_id,
                    'name': f"{subscription.customer.user.first_name} {subscription.customer.user.last_name}",
                    'phone': subscription.customer.user.phone,
                    'email': subscription.customer.user.email
                },
                'subscription': {
                    'id': subscription.id,
                    'subscription_number': subscription.subscription_number,
                    'plan_name': subscription.plan.name,
                    'end_date': subscription.end_date.isoformat(),
                    'days_remaining': days_remaining
                },
                'urgency': 'high' if days_remaining <= 3 else 'medium' if days_remaining <= 7 else 'low'
            })
        
        return {
            'reminders': reminders,
            'total': len(reminders),
            'by_urgency': {
                'high': len([r for r in reminders if r['urgency'] == 'high']),
                'medium': len([r for r in reminders if r['urgency'] == 'medium']),
                'low': len([r for r in reminders if r['urgency'] == 'low'])
            }
        }
