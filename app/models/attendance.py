"""Attendance model for gym entry tracking"""
from datetime import datetime, date, time
from app.database import db

class Attendance(db.Model):
    """Customer attendance records"""
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Customer and Branch
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    customer = db.relationship('Customer', back_populates='attendance_records')
    
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    branch = db.relationship('Branch')
    
    # Entry Details
    entry_date = db.Column(db.Date, default=date.today, nullable=False)
    entry_time = db.Column(db.Time, default=lambda: datetime.now().time(), nullable=False)
    exit_time = db.Column(db.Time)
    
    # Entry Method
    entry_method = db.Column(db.Enum('biometric', 'manual', 'card', name='entry_methods'), default='manual')
    biometric_verified = db.Column(db.Boolean, default=False)
    
    # Validation
    access_granted = db.Column(db.Boolean, default=True, nullable=False)
    denial_reason = db.Column(db.String(200))  # If access was denied
    
    # Staff who processed entry
    processed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    processed_by = db.relationship('User', foreign_keys=[processed_by_id])
    
    # Notes
    notes = db.Column(db.Text)
    
    # System Fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def calculate_duration(self):
        """Calculate workout duration"""
        if not self.exit_time:
            return None
        
        # Convert times to datetime for calculation
        entry_datetime = datetime.combine(date.today(), self.entry_time)
        exit_datetime = datetime.combine(date.today(), self.exit_time)
        
        # Handle case where exit is next day
        if exit_datetime < entry_datetime:
            exit_datetime = datetime.combine(date.today() + timedelta(days=1), self.exit_time)
        
        duration = exit_datetime - entry_datetime
        return duration.total_seconds() / 60  # Return duration in minutes
    
    def mark_exit(self, exit_time=None):
        """Mark customer exit"""
        if not exit_time:
            exit_time = datetime.now().time()
        
        self.exit_time = exit_time
        return True, "Exit marked successfully"
    
    def to_dict(self, include_customer=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'customer_id': self.customer_id,
            'branch_id': self.branch_id,
            'entry_date': self.entry_date.isoformat() if self.entry_date else None,
            'entry_time': self.entry_time.strftime('%H:%M:%S') if self.entry_time else None,
            'exit_time': self.exit_time.strftime('%H:%M:%S') if self.exit_time else None,
            'entry_method': self.entry_method,
            'biometric_verified': self.biometric_verified,
            'access_granted': self.access_granted,
            'denial_reason': self.denial_reason,
            'processed_by_id': self.processed_by_id,
            'notes': self.notes,
            'duration_minutes': self.calculate_duration(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_customer and self.customer:
            data['customer'] = {
                'member_id': self.customer.member_id,
                'name': f"{self.customer.user.first_name} {self.customer.user.last_name}"
            }
        
        return data
    
    def __repr__(self):
        return f'<Attendance {self.customer.member_id} - {self.entry_date} {self.entry_time}>'


class AttendanceValidation:
    """Service class for attendance validation logic"""
    
    @staticmethod
    def validate_entry(customer_id, branch_id=None):
        """Validate if customer can enter the gym"""
        from app.models.customer import Customer
        from app.models.subscription import Subscription
        
        customer = Customer.query.get(customer_id)
        if not customer:
            return False, "Customer not found"
        
        if not customer.is_active:
            return False, "Customer account is inactive"
        
        # Check for active subscription
        active_subscription = Subscription.query.filter_by(
            customer_id=customer_id,
            status='active'
        ).filter(
            Subscription.start_date <= date.today(),
            Subscription.end_date >= date.today()
        ).first()
        
        if not active_subscription:
            return False, "No active subscription found"
        
        # Check subscription access
        access_allowed, reason = active_subscription.is_access_allowed()
        if not access_allowed:
            return False, reason
        
        # Check branch access (if specified)
        if branch_id and active_subscription.branch_id != branch_id:
            return False, "Subscription not valid for this branch"
        
        # Check if already checked in today
        today_entry = Attendance.query.filter_by(
            customer_id=customer_id,
            entry_date=date.today(),
            access_granted=True,
            exit_time=None
        ).first()
        
        if today_entry:
            return False, "Customer already checked in today"
        
        return True, "Access granted"
    
    @staticmethod
    def record_entry(customer_id, branch_id, entry_method='manual', processed_by_id=None, notes=None):
        """Record customer entry after validation"""
        # Validate entry first
        is_valid, reason = AttendanceValidation.validate_entry(customer_id, branch_id)
        
        # Create attendance record
        attendance = Attendance(
            customer_id=customer_id,
            branch_id=branch_id,
            entry_method=entry_method,
            access_granted=is_valid,
            denial_reason=None if is_valid else reason,
            processed_by_id=processed_by_id,
            notes=notes
        )
        
        # Set biometric verification based on entry method
        if entry_method == 'biometric':
            attendance.biometric_verified = True
        
        db.session.add(attendance)
        db.session.commit()
        
        return attendance, is_valid, reason
