"""Payment model for financial transactions"""
from datetime import datetime, date
from sqlalchemy import Numeric
from app.database import db

class Payment(db.Model):
    """Payment transactions"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Payment Details
    payment_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    amount = db.Column(Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.Enum('cash', 'card', 'upi', 'net_banking', 'transfer', name='payment_methods'), nullable=False)
    
    # Status
    status = db.Column(db.Enum('pending', 'completed', 'failed', 'refunded', name='payment_status'), 
                      default='pending', nullable=False)
    
    # References
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'), nullable=True)
    subscription = db.relationship('Subscription', back_populates='payments')
    
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    customer = db.relationship('Customer')
    
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    branch = db.relationship('Branch')
    
    # Payment Processing
    payment_date = db.Column(db.Date, default=date.today, nullable=False)
    payment_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Additional Details
    service_type = db.Column(db.String(50))  # subscription, training, merchandise, etc.
    description = db.Column(db.String(200))
    reference_number = db.Column(db.String(100))  # Bank reference, UPI ID, etc.
    
    # Staff Information
    processed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    processed_by = db.relationship('User', foreign_keys=[processed_by_id])
    
    # Refund Information
    refund_date = db.Column(db.Date)
    refund_reason = db.Column(db.String(200))
    refund_processed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    refund_processed_by = db.relationship('User', foreign_keys=[refund_processed_by_id])
    
    # System Fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def process_payment(self):
        """Mark payment as completed"""
        if self.status == 'pending':
            self.status = 'completed'
            self.payment_time = datetime.utcnow()
            
            # Auto-activate subscription if payment is complete
            if self.subscription:
                self.subscription.activate_subscription()
            
            return True, "Payment processed successfully"
        return False, "Payment already processed or failed"
    
    def refund_payment(self, reason="Customer request", processed_by_id=None):
        """Process payment refund"""
        if self.status != 'completed':
            return False, "Only completed payments can be refunded"
        
        self.status = 'refunded'
        self.refund_date = date.today()
        self.refund_reason = reason
        self.refund_processed_by_id = processed_by_id
        
        return True, "Payment refunded successfully"
    
    def to_dict(self, include_customer=False, include_subscription=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'payment_number': self.payment_number,
            'amount': float(self.amount),
            'payment_method': self.payment_method,
            'status': self.status,
            'customer_id': self.customer_id,
            'subscription_id': self.subscription_id,
            'branch_id': self.branch_id,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'payment_time': self.payment_time.isoformat() if self.payment_time else None,
            'service_type': self.service_type,
            'description': self.description,
            'reference_number': self.reference_number,
            'processed_by_id': self.processed_by_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if self.status == 'refunded':
            data['refund_date'] = self.refund_date.isoformat() if self.refund_date else None
            data['refund_reason'] = self.refund_reason
            data['refund_processed_by_id'] = self.refund_processed_by_id
        
        if include_customer and self.customer:
            data['customer'] = {
                'member_id': self.customer.member_id,
                'name': f"{self.customer.user.first_name} {self.customer.user.last_name}"
            }
        
        if include_subscription and self.subscription:
            data['subscription'] = {
                'subscription_number': self.subscription.subscription_number,
                'plan_name': self.subscription.plan.name
            }
        
        return data
    
    def __repr__(self):
        return f'<Payment {self.payment_number} - ₹{self.amount} ({self.status})>'


class PaymentAuditLog(db.Model):
    """Audit log for payment operations"""
    __tablename__ = 'payment_audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=False)
    payment = db.relationship('Payment')
    
    action = db.Column(db.String(50), nullable=False)  # created, processed, refunded, etc.
    old_status = db.Column(db.String(20))
    new_status = db.Column(db.String(20))
    
    performed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    performed_by = db.relationship('User', foreign_keys=[performed_by_id])
    
    notes = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'payment_id': self.payment_id,
            'action': self.action,
            'old_status': self.old_status,
            'new_status': self.new_status,
            'performed_by_id': self.performed_by_id,
            'notes': self.notes,
            'timestamp': self.timestamp.isoformat()
        }
    
    def __repr__(self):
        return f'<PaymentAuditLog {self.action} - Payment {self.payment_id}>'
