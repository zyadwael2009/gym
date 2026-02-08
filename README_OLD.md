# Flask Gym Management System

A complete multi-branch gym management system built with Flask, designed for production use with comprehensive features for subscription management, customer tracking, payment processing, and multi-role access control.

## 🏋️ Features

### Core Functionality
- **Multi-Branch Management**: Centralized system supporting multiple gym branches
- **Role-Based Access Control**: Owner, Branch Manager, Receptionist, Accountant, and Customer roles
- **Subscription Management**: Flexible subscription plans with automated tracking
- **Payment Processing**: Complete payment history and transaction management
- **Attendance Tracking**: Real-time check-in/out with validation
- **Customer Management**: Comprehensive customer profiles and health tracking
- **Complaint System**: Customer feedback and resolution tracking
- **Dashboard Analytics**: Role-specific dashboards with key metrics

### Technical Features
- JWT-based authentication with secure token management
- RESTful API design with comprehensive error handling
- SQLAlchemy ORM with PostgreSQL/SQLite support
- Database migrations with Flask-Migrate
- Manual testing interface with HTML forms
- Modular blueprint architecture
- Production-ready configuration management

## 🛠️ Tech Stack

- **Backend**: Python 3.8+, Flask 2.3.3
- **Database**: PostgreSQL (production), SQLite (development)
- **ORM**: SQLAlchemy with Flask-SQLAlchemy
- **Authentication**: JWT with Flask-JWT-Extended
- **Migration**: Flask-Migrate
- **Testing**: HTML templates for manual API testing
- **Environment**: Python-dotenv for configuration

## 📋 Requirements

- Python 3.8 or higher
- PostgreSQL (for production) or SQLite (for development)
- Virtual environment (recommended)

## 🚀 Quick Start

### 1. Clone and Setup Environment

```bash
git clone <repository-url>
cd gym
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy environment template
copy .env.example .env

# Edit .env file with your configuration
# For development, SQLite will be used automatically
```

### 4. Initialize Database

```bash
# Initialize database and run migrations
flask db-init

# Seed database with sample data
flask seed-data
```

### 5. Run Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 🔧 Configuration

### Environment Variables (.env)

```env
# Application
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key

# Database (PostgreSQL for production)
DATABASE_URL=postgresql://username:password@localhost/gym_db

# Development (SQLite - automatically used if DATABASE_URL not set)
# SQLite database will be created automatically as gym.db

# JWT Configuration
JWT_ACCESS_TOKEN_EXPIRES=3600  # 1 hour
```

### Database Configuration

The application supports both PostgreSQL (production) and SQLite (development):

- **Production**: Set `DATABASE_URL` in environment
- **Development**: Leave `DATABASE_URL` unset to use SQLite automatically

## 👥 User Roles & Default Accounts

After seeding the database, the following accounts are available:

### System Owner
- **Email**: owner@gym.com
- **Password**: owner123
- **Access**: All branches, all features

### Branch Managers
- **Downtown**: manager.downtown@gym.com / manager123
- **Uptown**: manager.uptown@gym.com / manager123
- **Westside**: manager.westside@gym.com / manager123

### Staff Members
- **Receptionist**: receptionist@gym.com / receptionist123
- **Accountant**: accountant@gym.com / accountant123

### Customer
- **Email**: john.customer@gym.com
- **Password**: customer123

## 🌐 API Documentation

### Authentication Endpoints

#### POST /api/auth/login
Login with email and password to receive JWT token.

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "password123"
}
```

**Response:**
```json
{
    "access_token": "jwt-token-here",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "role": "owner",
        "branch_id": null
    }
}
```

#### POST /api/auth/logout
Logout and invalidate JWT token.

**Headers:**
```
Authorization: Bearer jwt-token-here
```

### Branch Management

#### GET /api/branches
List all branches (Owner access) or user's branch.

#### POST /api/branches
Create new branch (Owner only).

**Request Body:**
```json
{
    "name": "Branch Name",
    "address": "Branch Address",
    "phone": "123-456-7890"
}
```

#### GET /api/branches/{branch_id}
Get specific branch details.

#### PUT /api/branches/{branch_id}
Update branch information (Owner/Manager access).

### Customer Management

#### GET /api/customers
List customers for user's accessible branches.

#### POST /api/customers
Create new customer.

**Request Body:**
```json
{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "123-456-7890",
    "date_of_birth": "1990-01-01",
    "address": "123 Main St",
    "emergency_contact": "Jane Doe - 098-765-4321"
}
```

#### GET /api/customers/{customer_id}
Get customer details with subscription and attendance history.

#### PUT /api/customers/{customer_id}
Update customer information.

### Subscription Management

#### GET /api/subscriptions
List subscription plans or customer subscriptions.

#### POST /api/subscriptions
Create new subscription for customer.

**Request Body:**
```json
{
    "customer_id": 1,
    "plan_name": "Monthly Premium",
    "duration_months": 1,
    "price": 99.99
}
```

#### GET /api/subscriptions/{subscription_id}
Get subscription details.

#### PUT /api/subscriptions/{subscription_id}/status
Update subscription status (active/cancelled/suspended).

### Payment Management

#### GET /api/payments
List payments for accessible branches.

#### POST /api/payments
Record new payment.

**Request Body:**
```json
{
    "subscription_id": 1,
    "amount": 99.99,
    "payment_method": "cash"
}
```

#### GET /api/payments/{payment_id}
Get payment details.

### Attendance Tracking

#### POST /api/attendance/checkin
Customer check-in.

**Request Body:**
```json
{
    "customer_id": 1,
    "branch_id": 1
}
```

#### POST /api/attendance/checkout/{attendance_id}
Customer check-out.

#### GET /api/attendance/customer/{customer_id}
Get customer's attendance history.

### Dashboard & Analytics

#### GET /api/dashboard/overview
Get dashboard metrics for user's accessible branches.

**Response includes:**
- Total customers
- Active subscriptions
- Revenue statistics
- Recent activities

### Complaint Management

#### GET /api/complaints
List complaints for accessible branches.

#### POST /api/complaints
Submit new complaint.

**Request Body:**
```json
{
    "customer_id": 1,
    "branch_id": 1,
    "subject": "Equipment Issue",
    "description": "Treadmill not working properly"
}
```

#### PUT /api/complaints/{complaint_id}/resolve
Resolve complaint.

## 🧪 Testing Interface

Access the manual testing interface at `http://localhost:5000/test` to:

- Test all API endpoints with HTML forms
- View response data in formatted tables
- Switch between different user roles
- Manage test data without external tools

### Available Test Pages

- **Authentication**: Login/logout functionality
- **Branch Management**: CRUD operations for branches
- **Customer Management**: Customer registration and management
- **Subscriptions**: Plan management and customer subscriptions
- **Payments**: Payment recording and history
- **Attendance**: Check-in/out tracking
- **Complaints**: Customer feedback system
- **Dashboard**: Analytics and reporting

## 🗄️ Database Schema

### Core Tables

- **users**: System users with role-based access
- **branches**: Gym locations
- **customers**: Gym members
- **subscriptions**: Customer subscription plans
- **payments**: Payment transactions
- **attendance**: Check-in/out records
- **complaints**: Customer feedback

### Key Relationships

- Users belong to branches (except Owners)
- Customers can have multiple subscriptions
- Subscriptions have multiple payments
- Attendance records link customers to branches
- Complaints are branch and customer specific

## 📁 Project Structure

```
gym/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── branch.py
│   │   ├── customer.py
│   │   ├── subscription.py
│   │   ├── payment.py
│   │   ├── attendance.py
│   │   └── complaint.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── branch.py
│   │   ├── customer.py
│   │   ├── subscription.py
│   │   ├── payment.py
│   │   ├── attendance.py
│   │   ├── dashboard.py
│   │   └── complaint.py
│   ├── auth/
│   │   ├── __init__.py
│   │   └── decorators.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── subscription_service.py
│   │   └── notification_service.py
│   └── test_pages/
│       ├── __init__.py
│       ├── routes.py
│       └── templates/
├── migrations/
├── app.py
├── config.py
├── database.py
├── seed_data.py
├── requirements.txt
├── .env.example
└── README.md
```

## 🔐 Security Features

- JWT token-based authentication
- Role-based access control with branch isolation
- Password hashing with secure defaults
- Request validation and sanitization
- SQL injection prevention through ORM
- CORS configuration for API access

## 🚀 Production Deployment

### Database Setup

1. Create PostgreSQL database
2. Set `DATABASE_URL` environment variable
3. Run migrations: `flask db upgrade`
4. Seed initial data: `flask seed-data`

### Application Deployment

1. Use production WSGI server (Gunicorn, uWSGI)
2. Configure reverse proxy (Nginx, Apache)
3. Set up SSL certificates
4. Configure environment variables
5. Set up monitoring and logging

### Environment Configuration

```bash
# Production environment variables
export SECRET_KEY="production-secret-key"
export JWT_SECRET_KEY="production-jwt-secret"
export DATABASE_URL="postgresql://user:pass@localhost/gym_prod"
export FLASK_ENV="production"
```

## 📝 CLI Commands

The application includes custom CLI commands for database management:

```bash
# Initialize database and run migrations
flask db-init

# Seed database with sample data
flask seed-data
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the testing interface for API examples
- Review the comprehensive API documentation above

## 🎯 Development Notes

- All business logic is encapsulated in service classes
- API endpoints return JSON responses with consistent error handling
- Database relationships are carefully designed for data integrity
- Role-based access control ensures data security
- Modular architecture allows for easy feature extensions

---

Built with ❤️ using Flask and modern Python practices.