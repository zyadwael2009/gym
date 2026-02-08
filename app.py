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
    CORS(app)
    
    # Import models to ensure they are registered
    from app.models import user, branch, customer, subscription, payment, attendance, complaint
    
    # Register blueprints
    from app.api import auth_bp, branch_bp, customer_bp, subscription_bp, payment_bp, attendance_bp, dashboard_bp, complaint_bp
    from app.test_pages.routes import test_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(branch_bp, url_prefix='/api/branches')
    app.register_blueprint(customer_bp, url_prefix='/api/customers')
    app.register_blueprint(subscription_bp, url_prefix='/api/subscriptions')
    app.register_blueprint(payment_bp, url_prefix='/api/payments')
    app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(complaint_bp, url_prefix='/api/complaints')
    app.register_blueprint(test_bp, url_prefix='/test')
    
    # Register CLI commands
    from database import register_cli_commands
    from seed_data import register_seed_command
    register_cli_commands(app)
    register_seed_command(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    # Listen on all network interfaces (0.0.0.0) to allow connections from phone
    # Access via: http://192.168.1.6:5000 from phone
    # Access via: http://127.0.0.1:5000 from computer
    app.run(host='0.0.0.0', port=5000, debug=True)
