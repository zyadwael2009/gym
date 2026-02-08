# Gym Management System - Backend API

A comprehensive Flask-based REST API for managing gym operations including branches, customers, subscriptions, payments, attendance, and more.

## 🏗️ System Architecture

### Roles & Access Levels
- **👑 Owner**: Full system access, all branches
- **🏢 Branch Manager**: Branch-specific management
- **🎫 Receptionist**: Customer registration, subscriptions, check-ins
- **💰 Accountant**: Financial operations and reports
- **🏋️ Customer**: Member access (via mobile app)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/gym-backend.git
cd gym-backend
```

2. **Create virtual environment**
```bash
python -m venv venv
```

3. **Activate virtual environment**
- Windows:
  ```bash
  venv\Scripts\activate
  ```
- Linux/Mac:
  ```bash
  source venv/bin/activate
  ```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Initialize database with test data**
```bash
python seed.py
```

6. **Run the server**
```bash
python app.py
```

The server will start at `http://0.0.0.0:5000`

## 📱 Test Credentials

After running `seed.py`, you can login with these accounts:

| Role | Username | Password | Email |
|------|----------|----------|-------|
| 👑 Owner | owner | owner123 | owner@gym.com |
| 🏢 Manager | manager | manager123 | manager@gym.com |
| 🎫 Receptionist | receptionist | receptionist123 | receptionist@gym.com |
| 💰 Accountant | accountant | accountant123 | accountant@gym.com |
| 🏋️ Customer | customer | customer123 | customer@gym.com |

## 📚 API Documentation

### Authentication

**Login**
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "owner",
  "password": "owner123"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "owner",
    "role": "owner",
    "email": "owner@gym.com"
  }
}
```

### Protected Endpoints

All protected endpoints require the JWT token in the Authorization header:
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Main API Routes

#### 🏢 Branches
- `GET /api/branches` - List all branches
- `POST /api/branches` - Create new branch (Owner only)
- `GET /api/branches/<id>` - Get branch details
- `PUT /api/branches/<id>` - Update branch
- `DELETE /api/branches/<id>` - Delete/deactivate branch (Owner only)

#### 👥 Customers
- `GET /api/customers` - List customers
- `POST /api/customers` - Register new customer
- `GET /api/customers/<id>` - Get customer details
- `PUT /api/customers/<id>` - Update customer
- `DELETE /api/customers/<id>` - Deactivate customer

#### 📋 Subscriptions
- `GET /api/subscriptions` - List subscriptions
- `POST /api/subscriptions` - Create subscription
- `GET /api/subscriptions/<id>` - Get subscription details
- `PUT /api/subscriptions/<id>` - Update subscription
- `POST /api/subscriptions/<id>/suspend` - Suspend subscription
- `POST /api/subscriptions/<id>/activate` - Activate subscription

#### 💳 Payments
- `GET /api/payments` - List payments
- `POST /api/payments` - Record payment
- `GET /api/payments/<id>` - Get payment details

#### 📊 Dashboard
- `GET /api/dashboard/owner` - Owner dashboard
- `GET /api/dashboard/manager` - Branch manager dashboard
- `GET /api/dashboard/receptionist` - Receptionist dashboard
- `GET /api/dashboard/accountant` - Accountant dashboard

#### 📅 Attendance
- `POST /api/attendance/checkin` - Customer check-in
- `GET /api/attendance` - Get attendance records

#### 📝 Complaints
- `POST /api/complaints` - Submit complaint
- `GET /api/complaints` - List complaints
- `PUT /api/complaints/<id>` - Update complaint status

## 🗄️ Database Schema

### Core Models
- **User**: Authentication and role management
- **Branch**: Gym locations
- **Customer**: Member profiles with health data
- **Subscription**: Membership plans and status
- **Payment**: Financial transactions
- **Attendance**: Check-in/check-out records
- **Complaint**: Customer feedback and issues

## 🛠️ Technology Stack

- **Framework**: Flask 2.3.x
- **Database**: SQLite (SQLAlchemy ORM)
- **Authentication**: JWT (Flask-JWT-Extended)
- **CORS**: Flask-CORS
- **Migration**: Flask-Migrate

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── auth.py
│   │   ├── branch.py
│   │   ├── customer.py
│   │   ├── subscription.py
│   │   ├── payment.py
│   │   ├── attendance.py
│   │   ├── dashboard.py
│   │   └── complaint.py
│   ├── models/
│   │   ├── user.py
│   │   ├── branch.py
│   │   ├── customer.py
│   │   ├── subscription.py
│   │   ├── payment.py
│   │   ├── attendance.py
│   │   └── complaint.py
│   └── database.py
├── app.py
├── config.py
├── seed.py
├── requirements.txt
└── .gitignore
```

## 🔒 Security Features

- JWT-based authentication
- Role-based access control (RBAC)
- Password hashing with Werkzeug
- CORS protection
- Input validation
- SQL injection protection (SQLAlchemy ORM)

## 🧪 Testing

Run the seed script to reset database with test data:
```bash
python seed.py
```

## 📝 Environment Configuration

Create a `.env` file for production settings:
```env
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
DATABASE_URL=sqlite:///gym_management.db
FLASK_ENV=production
```

## 🌐 Network Configuration

The server runs on all network interfaces (`0.0.0.0:5000`) to allow:
- Local access: `http://127.0.0.1:5000`
- Network access: `http://192.168.1.6:5000` (replace with your IP)
- Mobile app connection from same network

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Developer

**زياد وائل لطفى مصطفى**
- Email: zwaellotfy@ams-benha.com

## 📞 Support

For support, email zwaellotfy@ams-benha.com or open an issue in the GitHub repository.

---

**Note**: This is a development version. For production deployment:
- Use a production WSGI server (Gunicorn, uWSGI)
- Use PostgreSQL or MySQL instead of SQLite
- Set up proper environment variables
- Enable HTTPS
- Implement rate limiting
- Add comprehensive logging

