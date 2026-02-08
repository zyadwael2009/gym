"""Subscription business logic service"""
from datetime import date, datetime, timedelta
from app.database import db
from app.models.subscription import Subscription, SubscriptionPlan, SubscriptionFreeze
from app.models.customer import Customer
from app.models.payment import Payment

class SubscriptionService:
    """Business logic for subscription management"""
    
    @staticmethod
    def check_expiring_subscriptions(days_ahead=7, branch_id=None):
        """Check for subscriptions expiring within specified days"""
        cutoff_date = date.today() + timedelta(days=days_ahead)
        
        query = Subscription.query.filter(
            Subscription.status == 'active',
            Subscription.end_date <= cutoff_date,
            Subscription.end_date >= date.today()
        )
        
        if branch_id:
            query = query.filter(Subscription.branch_id == branch_id)
        
        return query.order_by(Subscription.end_date.asc()).all()
    
    @staticmethod
    def auto_expire_subscriptions():
        """Auto-expire subscriptions that have passed their end date"""
        expired_subscriptions = Subscription.query.filter(
            Subscription.status == 'active',
            Subscription.end_date < date.today()
        ).all()
        
        expired_count = 0
        for subscription in expired_subscriptions:
            subscription.status = 'expired'
            expired_count += 1
        
        if expired_count > 0:
            db.session.commit()
        
        return expired_count
    
    @staticmethod
    def auto_unfreeze_subscriptions():
        """Auto-unfreeze subscriptions where freeze period has ended"""
        today = date.today()
        
        frozen_subscriptions = Subscription.query.filter(
            Subscription.status == 'frozen',
            Subscription.current_freeze_end < today
        ).all()
        
        unfrozen_count = 0
        for subscription in frozen_subscriptions:
            subscription.unfreeze_subscription()
            unfrozen_count += 1
        
        if unfrozen_count > 0:
            db.session.commit()
        
        return unfrozen_count
    
    @staticmethod
    def get_subscription_analytics(branch_id=None, start_date=None, end_date=None):
        """Get subscription analytics for reporting"""
        if not start_date:
            start_date = date.today().replace(day=1)  # Current month start
        if not end_date:
            end_date = date.today()
        
        query = Subscription.query.filter(
            Subscription.created_at >= start_date,
            Subscription.created_at <= end_date
        )
        
        if branch_id:
            query = query.filter(Subscription.branch_id == branch_id)
        
        subscriptions = query.all()
        
        # Calculate metrics
        total_subscriptions = len(subscriptions)
        active_subscriptions = len([s for s in subscriptions if s.status == 'active'])
        revenue = sum(float(s.actual_price) for s in subscriptions if s.is_payment_complete())
        
        # Plan popularity
        plan_stats = {}
        for subscription in subscriptions:
            plan_name = subscription.plan.name
            if plan_name not in plan_stats:
                plan_stats[plan_name] = 0
            plan_stats[plan_name] += 1
        
        return {
            'total_subscriptions': total_subscriptions,
            'active_subscriptions': active_subscriptions,
            'total_revenue': revenue,
            'plan_popularity': plan_stats,
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
        }
    
    @staticmethod
    def suggest_renewal_plans(customer_id):
        """Suggest renewal plans for a customer based on history"""
        customer = Customer.query.get(customer_id)
        if not customer:
            return []
        
        # Get customer's subscription history
        past_subscriptions = Subscription.query.filter_by(
            customer_id=customer_id
        ).order_by(Subscription.created_at.desc()).limit(3).all()
        
        if not past_subscriptions:
            # New customer - suggest popular plans
            popular_plans = SubscriptionPlan.query.filter_by(is_active=True).all()
            return [plan.to_dict() for plan in popular_plans[:3]]
        
        # Get most recent subscription plan
        recent_plan = past_subscriptions[0].plan
        
        # Suggest similar duration plans or same plan
        suggested_plans = SubscriptionPlan.query.filter(
            SubscriptionPlan.is_active == True,
            SubscriptionPlan.duration_days.in_([
                recent_plan.duration_days - 30,  # Shorter
                recent_plan.duration_days,       # Same
                recent_plan.duration_days + 30   # Longer
            ])
        ).all()
        
        return [plan.to_dict() for plan in suggested_plans]
    
    @staticmethod
    def validate_subscription_upgrade(subscription_id, new_plan_id):
        """Validate if subscription can be upgraded to new plan"""
        subscription = Subscription.query.get(subscription_id)
        new_plan = SubscriptionPlan.query.get(new_plan_id)
        
        if not subscription or not new_plan:
            return False, "Subscription or plan not found"
        
        if subscription.status != 'active':
            return False, "Only active subscriptions can be upgraded"
        
        if new_plan.price <= subscription.plan.price:
            return False, "New plan must be of higher value for upgrade"
        
        return True, "Upgrade allowed"
    
    @staticmethod
    def process_subscription_upgrade(subscription_id, new_plan_id, processed_by_id):
        """Process subscription upgrade with pro-rated pricing"""
        is_valid, message = SubscriptionService.validate_subscription_upgrade(
            subscription_id, new_plan_id
        )
        
        if not is_valid:
            return False, message, None
        
        subscription = Subscription.query.get(subscription_id)
        new_plan = SubscriptionPlan.query.get(new_plan_id)
        
        # Calculate pro-rated amount
        remaining_days = (subscription.end_date - date.today()).days
        if remaining_days <= 0:
            return False, "Subscription has expired", None
        
        # Simple pro-rating calculation
        old_daily_rate = float(subscription.actual_price) / subscription.plan.duration_days
        new_daily_rate = float(new_plan.price) / new_plan.duration_days
        
        refund_amount = old_daily_rate * remaining_days
        new_amount = new_daily_rate * remaining_days
        upgrade_amount = new_amount - refund_amount
        
        # Create new subscription for upgrade
        new_subscription = Subscription(
            customer_id=subscription.customer_id,
            plan_id=new_plan_id,
            branch_id=subscription.branch_id,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=remaining_days),
            actual_price=upgrade_amount,
            created_by_id=processed_by_id
        )
        
        # Cancel old subscription
        subscription.cancel_subscription("Upgraded to higher plan")
        
        try:
            db.session.add(new_subscription)
            db.session.commit()
            
            return True, "Upgrade processed successfully", {
                'new_subscription': new_subscription.to_dict(),
                'upgrade_amount': float(upgrade_amount),
                'remaining_days': remaining_days
            }
        
        except Exception as e:
            db.session.rollback()
            return False, f"Upgrade failed: {str(e)}", None
