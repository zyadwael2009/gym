"""App package initialization"""
from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
from app.database import db

# Initialize extensions
migrate = Migrate()
jwt = JWTManager()

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Configure CORS to allow all origins (for Flutter mobile app and web)
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })

    # Import models to ensure they are registered
    from app.models import user, branch, customer, subscription, payment, attendance, complaint
    
    # Register blueprints
    from app.api import auth_bp, branch_bp, customer_bp, subscription_bp, payment_bp, attendance_bp, dashboard_bp, complaint_bp
    
    print("[DEBUG] Importing paymob blueprint...")
    try:
        from app.api.paymob import paymob_bp
        print("[DEBUG] Paymob blueprint imported successfully")
    except Exception as e:
        print(f"[ERROR] Failed to import paymob blueprint: {e}")
        import traceback
        traceback.print_exc()
        paymob_bp = None

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(branch_bp, url_prefix='/api/branches')
    app.register_blueprint(customer_bp, url_prefix='/api/customers')
    app.register_blueprint(subscription_bp, url_prefix='/api/subscriptions')
    app.register_blueprint(payment_bp, url_prefix='/api/payments')
    app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(complaint_bp, url_prefix='/api/complaints')
    
    if paymob_bp:
        app.register_blueprint(paymob_bp, url_prefix='/api/paymob')
        print("[DEBUG] Paymob blueprint registered at /api/paymob")
    else:
        print("[WARNING] Paymob blueprint not registered due to import error")

    return app