"""Customer model for gym members"""
from datetime import datetime, date
from sqlalchemy import Numeric
from app.database import db
import math

class Customer(db.Model):
    """Customer model for gym members"""
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Link to User account
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    user = db.relationship('User', back_populates='customer_profile')
    
    # Branch Association
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    branch = db.relationship('Branch', foreign_keys=[branch_id])
    
    # Personal Details
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.Enum('male', 'female', 'other', name='gender_types'))
    emergency_contact_name = db.Column(db.String(100))
    emergency_contact_phone = db.Column(db.String(20))
    
    # Health Information
    height_cm = db.Column(Numeric(5, 2))  # Height in centimeters
    weight_kg = db.Column(Numeric(5, 2))  # Weight in kilograms
    medical_conditions = db.Column(db.Text)  # JSON string or text
    fitness_goals = db.Column(db.Text)
    
    # System Fields
    member_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    joined_date = db.Column(db.Date, default=date.today, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscriptions = db.relationship('Subscription', back_populates='customer', cascade='all, delete-orphan')
    attendance_records = db.relationship('Attendance', back_populates='customer', cascade='all, delete-orphan')
    health_reports = db.relationship('HealthReport', back_populates='customer', cascade='all, delete-orphan')
    
    def calculate_bmi(self):
        """Calculate BMI from height and weight"""
        if not self.height_cm or not self.weight_kg:
            return None
        height_m = float(self.height_cm) / 100
        return float(self.weight_kg) / (height_m ** 2)
    
    def get_bmi_category(self):
        """Get BMI category"""
        bmi = self.calculate_bmi()
        if not bmi:
            return 'Unknown'
        
        if bmi < 18.5:
            return 'Underweight'
        elif bmi < 25:
            return 'Normal'
        elif bmi < 30:
            return 'Overweight'
        else:
            return 'Obese'
    
    def calculate_ideal_weight(self):
        """Calculate ideal weight using BMI 22 (middle of normal range)"""
        if not self.height_cm:
            return None
        height_m = float(self.height_cm) / 100
        return 22 * (height_m ** 2)
    
    def calculate_daily_calories(self):
        """Calculate daily calorie needs (Harris-Benedict equation)"""
        if not self.weight_kg or not self.height_cm or not self.date_of_birth:
            return None
        
        # Calculate age
        today = date.today()
        age = today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        
        weight = float(self.weight_kg)
        height = float(self.height_cm)
        
        if self.gender == 'male':
            bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        else:  # female or other
            bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
        
        # Assume moderate activity level (1.55 multiplier)
        return bmr * 1.55
    
    def get_age(self):
        """Calculate age from date of birth"""
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
    
    def generate_health_report(self):
        """Generate current health report"""
        return {
            'bmi': round(self.calculate_bmi(), 2) if self.calculate_bmi() else None,
            'bmi_category': self.get_bmi_category(),
            'ideal_weight_kg': round(self.calculate_ideal_weight(), 2) if self.calculate_ideal_weight() else None,
            'daily_calories': round(self.calculate_daily_calories(), 0) if self.calculate_daily_calories() else None,
            'age': self.get_age()
        }
    
    def to_dict(self, include_health=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'branch_id': self.branch_id,
            'member_id': self.member_id,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'emergency_contact_name': self.emergency_contact_name,
            'emergency_contact_phone': self.emergency_contact_phone,
            'height_cm': float(self.height_cm) if self.height_cm else None,
            'weight_kg': float(self.weight_kg) if self.weight_kg else None,
            'medical_conditions': self.medical_conditions,
            'fitness_goals': self.fitness_goals,
            'joined_date': self.joined_date.isoformat() if self.joined_date else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_health:
            data['health_report'] = self.generate_health_report()
        
        return data
    
    def __repr__(self):
        return f'<Customer {self.member_id}: {self.user.first_name} {self.user.last_name}>'


class HealthReport(db.Model):
    """Health report snapshots for customers"""
    __tablename__ = 'health_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    customer = db.relationship('Customer', back_populates='health_reports')
    
    # Measurements at time of report
    height_cm = db.Column(Numeric(5, 2), nullable=False)
    weight_kg = db.Column(Numeric(5, 2), nullable=False)
    
    # Calculated values
    bmi = db.Column(Numeric(5, 2))
    bmi_category = db.Column(db.String(20))
    ideal_weight_kg = db.Column(Numeric(5, 2))
    daily_calories = db.Column(db.Integer)
    
    # Report metadata
    report_date = db.Column(db.Date, default=date.today, nullable=False)
    notes = db.Column(db.Text)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'height_cm': float(self.height_cm),
            'weight_kg': float(self.weight_kg),
            'bmi': float(self.bmi) if self.bmi else None,
            'bmi_category': self.bmi_category,
            'ideal_weight_kg': float(self.ideal_weight_kg) if self.ideal_weight_kg else None,
            'daily_calories': self.daily_calories,
            'report_date': self.report_date.isoformat() if self.report_date else None,
            'notes': self.notes,
            'created_by_id': self.created_by_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<HealthReport {self.customer.member_id} - {self.report_date}>'
