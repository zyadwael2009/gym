"""API package initialization"""
from flask import Blueprint

# Import all blueprints
from .auth import auth_bp
from .branch import branch_bp
from .customer import customer_bp
from .subscription import subscription_bp
from .payment import payment_bp
from .attendance import attendance_bp
from .dashboard import dashboard_bp
from .complaint import complaint_bp

__all__ = [
    'auth_bp',
    'branch_bp', 
    'customer_bp',
    'subscription_bp',
    'payment_bp',
    'attendance_bp',
    'dashboard_bp',
    'complaint_bp'
]