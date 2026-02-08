"""Complaint model for customer feedback"""
from datetime import datetime, date
from app.database import db

class Complaint(db.Model):
    """Customer complaints and feedback"""
    __tablename__ = 'complaints'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Complaint Details
    complaint_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Categorization
    category = db.Column(db.Enum('service', 'cleanliness', 'equipment', 'staff', 'billing', 'other', name='complaint_categories'), nullable=False)
    priority = db.Column(db.Enum('low', 'medium', 'high', 'critical', name='complaint_priorities'), default='medium')
    
    # Customer and Branch
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    customer = db.relationship('Customer')
    
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    branch = db.relationship('Branch')
    
    # Status Management
    status = db.Column(db.Enum('open', 'in_progress', 'resolved', 'closed', name='complaint_status'), default='open')
    
    # Assignment
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id])
    assigned_date = db.Column(db.Date)
    
    # Resolution
    resolution_notes = db.Column(db.Text)
    resolved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    resolved_by = db.relationship('User', foreign_keys=[resolved_by_id])
    resolved_date = db.Column(db.Date)
    
    # Customer Satisfaction
    customer_rating = db.Column(db.Integer)  # 1-5 rating
    customer_feedback = db.Column(db.Text)
    
    # System Fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    updates = db.relationship('ComplaintUpdate', back_populates='complaint', cascade='all, delete-orphan')
    
    def assign_to_user(self, user_id):
        """Assign complaint to a user"""
        if self.status == 'closed':
            return False, "Cannot assign closed complaint"
        
        self.assigned_to_id = user_id
        self.assigned_date = date.today()
        if self.status == 'open':
            self.status = 'in_progress'
        
        return True, "Complaint assigned successfully"
    
    def resolve_complaint(self, resolution_notes, resolved_by_id):
        """Mark complaint as resolved"""
        if self.status == 'closed':
            return False, "Complaint is already closed"
        
        self.status = 'resolved'
        self.resolution_notes = resolution_notes
        self.resolved_by_id = resolved_by_id
        self.resolved_date = date.today()
        
        return True, "Complaint resolved successfully"
    
    def close_complaint(self, customer_rating=None, customer_feedback=None):
        """Close complaint with customer feedback"""
        if self.status != 'resolved':
            return False, "Complaint must be resolved before closing"
        
        self.status = 'closed'
        if customer_rating:
            self.customer_rating = customer_rating
        if customer_feedback:
            self.customer_feedback = customer_feedback
        
        return True, "Complaint closed successfully"
    
    def add_update(self, update_text, updated_by_id):
        """Add update to complaint"""
        update = ComplaintUpdate(
            complaint_id=self.id,
            update_text=update_text,
            updated_by_id=updated_by_id
        )
        db.session.add(update)
        return update
    
    def get_age_days(self):
        """Get complaint age in days"""
        return (date.today() - self.created_at.date()).days
    
    def to_dict(self, include_updates=False, include_customer=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'complaint_number': self.complaint_number,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'priority': self.priority,
            'customer_id': self.customer_id,
            'branch_id': self.branch_id,
            'status': self.status,
            'assigned_to_id': self.assigned_to_id,
            'assigned_date': self.assigned_date.isoformat() if self.assigned_date else None,
            'resolution_notes': self.resolution_notes,
            'resolved_by_id': self.resolved_by_id,
            'resolved_date': self.resolved_date.isoformat() if self.resolved_date else None,
            'customer_rating': self.customer_rating,
            'customer_feedback': self.customer_feedback,
            'age_days': self.get_age_days(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_customer and self.customer:
            data['customer'] = {
                'member_id': self.customer.member_id,
                'name': f"{self.customer.user.first_name} {self.customer.user.last_name}",
                'phone': self.customer.user.phone
            }
        
        if include_updates:
            data['updates'] = [update.to_dict() for update in self.updates]
        
        return data
    
    def __repr__(self):
        return f'<Complaint {self.complaint_number} - {self.category} ({self.status})>'


class ComplaintUpdate(db.Model):
    """Updates/comments on complaints"""
    __tablename__ = 'complaint_updates'
    
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=False)
    complaint = db.relationship('Complaint', back_populates='updates')
    
    update_text = db.Column(db.Text, nullable=False)
    
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    updated_by = db.relationship('User')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'complaint_id': self.complaint_id,
            'update_text': self.update_text,
            'updated_by_id': self.updated_by_id,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<ComplaintUpdate {self.id} - Complaint {self.complaint_id}>'
