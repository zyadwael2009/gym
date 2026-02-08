# 🏋️ Flask Gym Management System - Complete Project Summary

## 📋 Project Overview

**Flask Gym Management System** is a comprehensive multi-branch gym management solution built with Flask. It provides role-based access control, subscription management, payment processing, attendance tracking, and customer management features.

**Current Status**: ✅ Fully Functional - Customer creation issue resolved, database seeded, test interface operational

---

## 🛠️ Tech Stack

### Backend Framework
- **Flask 2.3.3**: Web framework with modular blueprint architecture
- **SQLAlchemy 2.0.21**: ORM for database operations with relationship management
- **Flask-Migrate 4.0.5**: Database migration management
- **Flask-JWT-Extended 4.5.3**: JWT-based authentication with secure token management
- **Flask-CORS 4.0.0**: Cross-origin resource sharing support

### Database
- **Primary**: SQLite (development) / PostgreSQL (production)
- **ORM**: SQLAlchemy with relationship mapping and foreign key constraints
- **Migration**: Flask-Migrate for version control

### Security & Authentication
- **JWT Tokens**: Access and refresh token system
- **Password Hashing**: Werkzeug secure password storage
- **Role-Based Access**: Owner, Manager, Receptionist, Accountant, Customer roles
- **Branch-Level Security**: Users restricted to their assigned branches

### Development & Testing
- **Jinja2**: Template engine for manual testing interfaces
- **Click**: CLI commands for database operations
- **Python-dotenv**: Environment variable management

---

## 📁 Project Structure

```
gym/
├── app/
│   ├── __init__.py                 # Application factory
│   ├── database.py                 # Database instance
│   ├── auth.py                     # Authentication decorators
│   ├── models/                     # Database models
│   │   ├── user.py                 # User authentication & roles
│   │   ├── branch.py               # Gym branch management
│   │   ├── customer.py             # Customer profiles & health reports
│   │   ├── subscription.py         # Plans & subscriptions
│   │   ├── payment.py              # Payment processing & audit
│   │   ├── attendance.py           # Check-in/out tracking
│   │   └── complaint.py            # Customer feedback system
│   ├── api/                        # RESTful API endpoints
│   │   ├── auth.py                 # Login/logout/register
│   │   ├── branch.py               # Branch management
│   │   ├── customer.py             # Customer operations
│   │   ├── subscription.py         # Subscription management
│   │   ├── payment.py              # Payment processing
│   │   ├── attendance.py           # Attendance tracking
│   │   ├── dashboard.py            # Analytics & reporting
│   │   └── complaint.py            # Complaint handling
│   ├── test_pages/                 # Manual testing interface
│   │   ├── routes.py               # Test page routes
│   │   └── templates/              # HTML testing forms
│   └── services/                   # Business logic layer
├── seed_database.py                # Database seeding script
├── app.py                         # Application entry point
├── config.py                      # Configuration management
├── requirements.txt               # Python dependencies
└── README.md                      # Project documentation
```

---

## 🗄️ Database Schema

### Core Tables & Relationships

#### 1. **Users Table**
```sql
users (
    id: Primary Key,
    username: Unique String(80),
    email: Unique String(120),
    password_hash: String(255),
    role: Enum('owner', 'branch_manager', 'receptionist', 'accountant', 'customer'),
    first_name: String(50),
    last_name: String(50),
    phone: String(20),
    is_active: Boolean,
    branch_id: Foreign Key → branches.id,
    created_at: DateTime,
    updated_at: DateTime,
    last_login: DateTime
)
```

#### 2. **Branches Table**
```sql
branches (
    id: Primary Key,
    name: String(100),
    code: Unique String(10),
    address_line1: String(200),
    address_line2: String(200),
    city: String(100),
    state: String(100),
    pincode: String(10),
    phone: String(20),
    email: String(120),
    opening_time: Time,
    closing_time: Time,
    monthly_target: Decimal(10,2),
    is_active: Boolean,
    created_at: DateTime
)
```

#### 3. **Customers Table**
```sql
customers (
    id: Primary Key,
    user_id: Unique Foreign Key → users.id,
    branch_id: Foreign Key → branches.id,
    member_id: Unique String(20),
    date_of_birth: Date,
    gender: Enum('male', 'female', 'other'),
    emergency_contact_name: String(100),
    emergency_contact_phone: String(20),
    height_cm: Decimal(5,2),
    weight_kg: Decimal(5,2),
    medical_conditions: Text,
    fitness_goals: Text,
    joined_date: Date,
    is_active: Boolean,
    created_at: DateTime
)
```

#### 4. **Subscription Plans Table**
```sql
subscription_plans (
    id: Primary Key,
    name: String(100),
    description: Text,
    duration_days: Integer,
    price: Decimal(10,2),
    access_hours: String(50),
    includes_trainer: Boolean,
    includes_nutrition: Boolean,
    max_freeze_days: Integer,
    is_active: Boolean,
    created_at: DateTime
)
```

#### 5. **Subscriptions Table**
```sql
subscriptions (
    id: Primary Key,
    subscription_number: Unique String(50),
    customer_id: Foreign Key → customers.id,
    plan_id: Foreign Key → subscription_plans.id,
    branch_id: Foreign Key → branches.id,
    start_date: Date,
    end_date: Date,
    status: Enum('draft', 'active', 'expired', 'cancelled'),
    total_amount: Decimal(10,2),
    paid_amount: Decimal(10,2),
    created_by_id: Foreign Key → users.id,
    created_at: DateTime
)
```

#### 6. **Payments Table**
```sql
payments (
    id: Primary Key,
    payment_number: Unique String(50),
    customer_id: Foreign Key → customers.id,
    subscription_id: Foreign Key → subscriptions.id,
    amount: Decimal(10,2),
    payment_method: Enum('cash', 'card', 'upi', 'bank_transfer'),
    status: Enum('pending', 'completed', 'failed', 'refunded'),
    payment_date: Date,
    processed_by_id: Foreign Key → users.id,
    branch_id: Foreign Key → branches.id,
    created_at: DateTime
)
```

#### 7. **Attendance Table**
```sql
attendance (
    id: Primary Key,
    customer_id: Foreign Key → customers.id,
    branch_id: Foreign Key → branches.id,
    entry_date: Date,
    entry_time: Time,
    exit_time: Time,
    entry_method: Enum('biometric', 'manual', 'card'),
    biometric_verified: Boolean,
    access_granted: Boolean,
    created_at: DateTime
)
```

#### 8. **Complaints Table**
```sql
complaints (
    id: Primary Key,
    complaint_number: Unique String(50),
    customer_id: Foreign Key → customers.id,
    branch_id: Foreign Key → branches.id,
    title: String(200),
    description: Text,
    category: Enum('service', 'cleanliness', 'equipment', 'staff', 'billing', 'other'),
    priority: Enum('low', 'medium', 'high', 'critical'),
    status: Enum('open', 'in_progress', 'resolved', 'closed'),
    assigned_to_id: Foreign Key → users.id,
    resolved_by_id: Foreign Key → users.id,
    created_at: DateTime
)
```

#### 9. **Health Reports Table**
```sql
health_reports (
    id: Primary Key,
    customer_id: Foreign Key → customers.id,
    height_cm: Decimal(5,2),
    weight_kg: Decimal(5,2),
    bmi: Decimal(5,2),
    bmi_category: String(20),
    report_date: Date,
    notes: Text,
    created_by_id: Foreign Key → users.id,
    created_at: DateTime
)
```

---

## 🌐 API Endpoints

### Authentication Endpoints
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| `POST` | `/api/auth/login` | User login with username/email and password | Public |
| `POST` | `/api/auth/logout` | Logout and invalidate token | Authenticated |
| `POST` | `/api/auth/refresh` | Refresh access token | Refresh Token |
| `POST` | `/api/auth/register` | Register new user (admin only) | Owner |
| `POST` | `/api/auth/change-password` | Change user password | Authenticated |

### Branch Management
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| `GET` | `/api/branches` | List branches (filtered by role) | Staff |
| `POST` | `/api/branches` | Create new branch | Owner |
| `GET` | `/api/branches/{id}` | Get branch details | Staff |
| `PUT` | `/api/branches/{id}` | Update branch information | Manager+ |
| `DELETE` | `/api/branches/{id}` | Delete branch | Owner |
| `POST` | `/api/branches/{id}/assign-manager` | Assign manager to branch | Owner |
| `GET` | `/api/branches/{id}/staff` | Get branch staff members | Manager+ |

### Customer Management
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| `GET` | `/api/customers` | List customers (filtered by branch) | Staff |
| `POST` | `/api/customers` | Create new customer | Receptionist+ |
| `GET` | `/api/customers/{id}` | Get customer details | Staff |
| `PUT` | `/api/customers/{id}` | Update customer information | Receptionist+ |
| `POST` | `/api/customers/{id}/deactivate` | Deactivate customer account | Receptionist+ |
| `POST` | `/api/customers/{id}/health-report` | Create health report | Receptionist+ |
| `GET` | `/api/customers/{id}/health-reports` | Get health report history | Staff |

### Subscription Management
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| `GET` | `/api/subscriptions/plans` | List subscription plans | Staff |
| `POST` | `/api/subscriptions/plans` | Create subscription plan | Owner |
| `PUT` | `/api/subscriptions/plans/{id}` | Update subscription plan | Owner |
| `GET` | `/api/subscriptions` | List subscriptions | Staff |
| `POST` | `/api/subscriptions` | Create new subscription | Receptionist+ |
| `GET` | `/api/subscriptions/{id}` | Get subscription details | Staff |
| `POST` | `/api/subscriptions/{id}/activate` | Activate subscription | Receptionist+ |
| `POST` | `/api/subscriptions/{id}/freeze` | Freeze subscription | Receptionist+ |
| `POST` | `/api/subscriptions/{id}/unfreeze` | Resume frozen subscription | Receptionist+ |
| `POST` | `/api/subscriptions/{id}/cancel` | Cancel subscription | Receptionist+ |
| `POST` | `/api/subscriptions/{id}/renew` | Renew subscription | Receptionist+ |
| `GET` | `/api/subscriptions/expiring` | Get expiring subscriptions | Staff |

### Payment Management
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| `GET` | `/api/payments` | List payments (filtered by branch) | Staff |
| `POST` | `/api/payments` | Create payment record | Staff |
| `GET` | `/api/payments/{id}` | Get payment details | Staff |
| `POST` | `/api/payments/{id}/process` | Process/complete payment | Staff |
| `POST` | `/api/payments/{id}/refund` | Process refund | Accountant+ |

### Attendance Tracking
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| `POST` | `/api/attendance/validate` | Validate customer entry | Staff |
| `POST` | `/api/attendance/checkin` | Record customer check-in | Staff |
| `POST` | `/api/attendance/checkout` | Record customer check-out | Staff |
| `POST` | `/api/attendance/biometric-check` | Biometric verification | Staff |
| `GET` | `/api/attendance` | List attendance records | Staff |
| `GET` | `/api/attendance/today` | Today's attendance overview | Staff |
| `GET` | `/api/attendance/customer/{id}/history` | Customer attendance history | Staff |

### Dashboard & Analytics
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| `GET` | `/api/dashboard/owner` | System-wide analytics | Owner |
| `GET` | `/api/dashboard/branch/{id}` | Branch-specific dashboard | Manager+ |
| `GET` | `/api/dashboard/accountant` | Financial overview | Staff |

### Complaint Management
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| `GET` | `/api/complaints` | List complaints | Staff |
| `POST` | `/api/complaints` | Submit new complaint | Staff |
| `GET` | `/api/complaints/{id}` | Get complaint details | Staff |
| `POST` | `/api/complaints/{id}/assign` | Assign complaint to staff | Manager+ |
| `POST` | `/api/complaints/{id}/update` | Add update/comment | Staff |
| `POST` | `/api/complaints/{id}/resolve` | Mark complaint as resolved | Staff |
| `POST` | `/api/complaints/{id}/close` | Close resolved complaint | Manager+ |
| `GET` | `/api/complaints/summary` | Complaint statistics | Staff |

---

## 👥 User Roles & Permissions

### Role Hierarchy

#### 1. **Owner**
- **Access**: All branches, all features, system-wide analytics
- **Permissions**: 
  - Create/modify branches and subscription plans
  - Assign branch managers
  - View system-wide reports and analytics
  - Complete administrative control

#### 2. **Branch Manager**
- **Access**: Assigned branch only
- **Permissions**:
  - Manage branch operations and staff
  - View branch analytics and reports
  - Handle customer escalations
  - Assign/close complaints

#### 3. **Receptionist**
- **Access**: Assigned branch only
- **Permissions**:
  - Customer registration and management
  - Subscription creation and management
  - Payment processing
  - Attendance tracking
  - Basic complaint handling

#### 4. **Accountant**
- **Access**: Assigned branch only
- **Permissions**:
  - Payment processing and refunds
  - Financial reporting
  - Payment audit and verification
  - Subscription billing

#### 5. **Customer**
- **Access**: Limited to own profile and data
- **Permissions**:
  - View personal subscription and payment history
  - Submit complaints and feedback
  - Update basic profile information

---

## 🗂️ Test Interface & Manual Testing

### Available Test Pages
- **Login**: `/test/login` - Authentication testing
- **Dashboard**: `/test/dashboard` - Role-based dashboard testing
- **Customer Management**: `/test/customers` - Customer creation and listing
- **Customer List**: `/test/customers/list` - View all customers

### Default Login Credentials
```
Owner:
  Email: owner@gym.com
  Password: owner123

Manager:
  Email: manager.downtown@gym.com  
  Password: manager123

Receptionist:
  Email: receptionist@gym.com
  Password: receptionist123

Accountant:
  Email: accountant@gym.com
  Password: accountant123
```

---

## 🏢 Sample Data Structure

### Pre-seeded Branches
1. **Downtown Gym** (Code: DT) - Main branch
2. **Uptown Fitness** (Code: UT) - Secondary branch  
3. **Westside Wellness** (Code: WS) - Wellness center

### Subscription Plans
1. **Basic Monthly** - ₹49.99/month (30 days)
2. **Premium Monthly** - ₹99.99/month (30 days)
3. **VIP Monthly** - ₹149.99/month (30 days)
4. **Annual Premium** - ₹999.99/year (365 days)

---

## 🔧 Development & Deployment

### Local Development Setup
1. **Install Dependencies**: `pip install -r requirements.txt`
2. **Database Setup**: `python seed_database.py`
3. **Run Application**: `python app.py`
4. **Access Test Interface**: `http://127.0.0.1:5000/test`

### Database Operations
```bash
# Create tables
python database.py create-tables

# Reset database
python database.py reset-db

# Seed with sample data
python seed_database.py
```

### API Testing
- **Base URL**: `http://127.0.0.1:5000/api`
- **Authentication**: Bearer token in Authorization header
- **Content-Type**: `application/json`

---

## 🔍 Key Features Implemented

### ✅ Authentication & Security
- JWT-based authentication with access/refresh tokens
- Role-based access control with branch-level restrictions
- Secure password hashing with Werkzeug
- Session management for test interfaces

### ✅ Customer Management
- Complete customer registration with health profiles
- Member ID generation with branch codes
- Health report tracking with BMI calculations
- Emergency contact management

### ✅ Subscription System
- Flexible subscription plans with custom durations
- Subscription lifecycle management (draft → active → expired)
- Freeze/unfreeze functionality for temporary suspensions
- Automatic renewal and cancellation handling

### ✅ Payment Processing
- Multi-method payment support (cash, card, UPI, bank transfer)
- Payment audit logging with staff tracking
- Refund processing with reason tracking
- Payment history and transaction management

### ✅ Attendance Tracking
- Real-time check-in/check-out with validation
- Biometric simulation support
- Daily attendance reporting
- Customer attendance history

### ✅ Complaint Management
- Categorized complaint system with priority levels
- Assignment workflow to appropriate staff
- Resolution tracking with customer feedback
- Complaint analytics and reporting

### ✅ Dashboard Analytics
- Role-specific dashboards with relevant metrics
- Branch performance analytics
- Financial reporting and insights
- Customer engagement tracking

---

## 🚀 Current Status

**Project Status**: ✅ **FULLY OPERATIONAL**

### Recently Resolved Issues
- ✅ Fixed SQLAlchemy relationship ambiguity errors
- ✅ Created comprehensive customer management test interface
- ✅ Successfully seeded database with sample data
- ✅ Resolved customer creation functionality
- ✅ Fixed syntax and import issues throughout codebase

### System Health
- **Database**: ✅ Operational with sample data
- **API Endpoints**: ✅ All endpoints functional
- **Authentication**: ✅ JWT system working properly
- **Test Interface**: ✅ Manual testing interface available
- **Role-Based Access**: ✅ Properly implemented and tested

### Ready for Use
The system is now fully functional and ready for:
- Customer registration and management
- Subscription plan creation and management
- Payment processing and tracking
- Attendance monitoring
- Complaint handling and resolution
- Multi-branch operations with role-based access

**Access the application**: `http://127.0.0.1:5000/test/customers` (login required)

---

*Last Updated: January 28, 2026*