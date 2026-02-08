"""Branch model for multi-branch management"""
from datetime import datetime
from sqlalchemy import Numeric
from app.database import db

class Branch(db.Model):
    """Branch model for gym locations"""
    __tablename__ = 'branches'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    
    # Address Information
    address_line1 = db.Column(db.String(200))
    address_line2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    pincode = db.Column(db.String(10))
    country = db.Column(db.String(100), default='India')
    
    # Contact Information
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    
    # Business Information
    opening_time = db.Column(db.Time)
    closing_time = db.Column(db.Time)
    monthly_target = db.Column(Numeric(10, 2), default=0)
    
    # System Fields
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Manager Assignment
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    manager = db.relationship('User', foreign_keys=[manager_id], post_update=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'address': {
                'line1': self.address_line1,
                'line2': self.address_line2,
                'city': self.city,
                'state': self.state,
                'pincode': self.pincode,
                'country': self.country
            },
            'phone': self.phone,
            'email': self.email,
            'opening_time': self.opening_time.strftime('%H:%M') if self.opening_time else None,
            'closing_time': self.closing_time.strftime('%H:%M') if self.closing_time else None,
            'monthly_target': float(self.monthly_target) if self.monthly_target else 0,
            'manager_id': self.manager_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Branch {self.code}: {self.name}>'
