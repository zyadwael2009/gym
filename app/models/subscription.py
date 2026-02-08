"""Subscription model for gym memberships"""
from datetime import datetime, date, timedelta
from sqlalchemy import Numeric
from app.database import db

class SubscriptionPlan(db.Model):
    """Subscription plans available"""
    __tablename__ = 'subscription_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    duration_days = db.Column(db.Integer, nullable=False)  # Duration in days
    price = db.Column(Numeric(10, 2), nullable=False)
    
    # Plan features
    access_hours = db.Column(db.String(50))  # e.g., '24x7', '6AM-10PM'
    includes_trainer = db.Column(db.Boolean, default=False)
    includes_nutrition = db.Column(db.Boolean, default=False)
    max_freeze_days = db.Column(db.Integer, default=0)
    
    # System fields
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscriptions = db.relationship('Subscription', back_populates='plan')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'duration_days': self.duration_days,
            'price': float(self.price),
            'access_hours': self.access_hours,
            'includes_trainer': self.includes_trainer,
            'includes_nutrition': self.includes_nutrition,
            'max_freeze_days': self.max_freeze_days,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<SubscriptionPlan {self.name} - {self.duration_days} days>'


class Subscription(db.Model):
    """Customer subscriptions"""
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Links
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    customer = db.relationship('Customer', back_populates='subscriptions')
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'), nullable=False)
    plan = db.relationship('SubscriptionPlan', back_populates='subscriptions')
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    branch = db.relationship('Branch')
    
    # Subscription Details
    subscription_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    actual_price = db.Column(Numeric(10, 2), nullable=False)  # Price at time of purchase
    
    # Status Management
    status = db.Column(db.Enum('pending', 'active', 'frozen', 'expired', 'cancelled', name='subscription_status'), 
                      default='pending', nullable=False)
    
    # Freeze Management
    total_freeze_days_used = db.Column(db.Integer, default=0)
    current_freeze_start = db.Column(db.Date, nullable=True)
    current_freeze_end = db.Column(db.Date, nullable=True)
    freeze_reason = db.Column(db.String(200))
    
    # Cancellation
    cancelled_date = db.Column(db.Date, nullable=True)
    cancellation_reason = db.Column(db.String(200))
    
    # Auto-extension (for recurring subscriptions)
    auto_renew = db.Column(db.Boolean, default=False)
    
    # System Fields
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    payments = db.relationship('Payment', back_populates='subscription')
    freeze_history = db.relationship('SubscriptionFreeze', back_populates='subscription', cascade='all, delete-orphan')
    
    def is_payment_complete(self):
        """Check if subscription is fully paid"""
        total_paid = sum(payment.amount for payment in self.payments if payment.status == 'completed')
        return total_paid >= self.actual_price
    
    def activate_subscription(self):
        """Activate subscription if payment is complete"""
        if self.is_payment_complete() and self.status == 'pending':
            self.status = 'active'
            return True
        return False
    
    def can_freeze(self, days_requested):
        """Check if subscription can be frozen"""
        if self.status != 'active':
            return False, "Subscription must be active to freeze"
        
        remaining_freeze_days = self.plan.max_freeze_days - self.total_freeze_days_used
        if days_requested > remaining_freeze_days:
            return False, f"Only {remaining_freeze_days} freeze days remaining"
        
        return True, "Can freeze subscription"
    
    def freeze_subscription(self, days, reason="Customer request"):
        """Freeze subscription for specified days"""
        can_freeze, message = self.can_freeze(days)
        if not can_freeze:
            return False, message
        
        today = date.today()
        freeze_end = today + timedelta(days=days)
        
        self.status = 'frozen'
        self.current_freeze_start = today
        self.current_freeze_end = freeze_end
        self.freeze_reason = reason
        self.total_freeze_days_used += days
        
        # Extend end date by freeze days
        self.end_date += timedelta(days=days)
        
        return True, "Subscription frozen successfully"
    
    def unfreeze_subscription(self):
        """Resume frozen subscription"""
        if self.status == 'frozen':
            self.status = 'active'
            self.current_freeze_start = None
            self.current_freeze_end = None
            self.freeze_reason = None
            return True, "Subscription resumed"
        return False, "Subscription is not frozen"
    
    def cancel_subscription(self, reason="Customer request"):
        """Cancel subscription"""
        if self.status in ['cancelled', 'expired']:
            return False, "Subscription already cancelled/expired"
        
        self.status = 'cancelled'
        self.cancelled_date = date.today()
        self.cancellation_reason = reason
        return True, "Subscription cancelled"
    
    def check_expiry(self):
        """Check and update expiry status"""
        today = date.today()
        if self.status == 'active' and today > self.end_date:
            self.status = 'expired'
            return True
        return False
    
    def is_access_allowed(self):
        """Check if customer has access today"""
        today = date.today()
        
        # Check if subscription is active
        if self.status != 'active':
            return False, f"Subscription is {self.status}"
        
        # Check if within subscription period
        if today < self.start_date or today > self.end_date:
            return False, "Outside subscription period"
        
        # Check if not frozen
        if self.current_freeze_start and self.current_freeze_end:
            if self.current_freeze_start <= today <= self.current_freeze_end:
                return False, "Subscription is frozen"
        
        return True, "Access allowed"
    
    def get_status_info(self):
        """Get detailed status information"""
        today = date.today()
        info = {
            'status': self.status,
            'days_remaining': (self.end_date - today).days if self.end_date >= today else 0,
            'is_paid': self.is_payment_complete(),
            'freeze_days_used': self.total_freeze_days_used,
            'freeze_days_available': self.plan.max_freeze_days - self.total_freeze_days_used
        }
        
        if self.status == 'frozen':
            info['freeze_ends'] = self.current_freeze_end.isoformat() if self.current_freeze_end else None
            info['freeze_reason'] = self.freeze_reason
        
        return info
    
    def to_dict(self, include_details=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'customer_id': self.customer_id,
            'plan_id': self.plan_id,
            'branch_id': self.branch_id,
            'subscription_number': self.subscription_number,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'actual_price': float(self.actual_price),
            'status': self.status,
            'auto_renew': self.auto_renew,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_details:
            data['status_info'] = self.get_status_info()
            data['plan'] = self.plan.to_dict() if self.plan else None
            data['total_paid'] = sum(p.amount for p in self.payments if p.status == 'completed')
        
        return data
    
    def __repr__(self):
        return f'<Subscription {self.subscription_number} - {self.status}>'


class SubscriptionFreeze(db.Model):
    """History of subscription freezes"""
    __tablename__ = 'subscription_freezes'
    
    id = db.Column(db.Integer, primary_key=True)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'), nullable=False)
    subscription = db.relationship('Subscription', back_populates='freeze_history')
    
    freeze_start = db.Column(db.Date, nullable=False)
    freeze_end = db.Column(db.Date, nullable=False)
    days_frozen = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(200))
    
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'freeze_start': self.freeze_start.isoformat(),
            'freeze_end': self.freeze_end.isoformat(),
            'days_frozen': self.days_frozen,
            'reason': self.reason,
            'created_by_id': self.created_by_id,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<SubscriptionFreeze {self.subscription.subscription_number} - {self.days_frozen} days>'
