# Quick Setup Guide

## 🏃‍♂️ Fast Track Setup (5 minutes)

### 1. Install & Setup
```bash
# Clone and enter directory
cd gym

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy environment file
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Edit .env file - for quick start, just set:
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key
# Leave DATABASE_URL empty to use SQLite
```

### 3. Initialize Database
```bash
# Setup database and add sample data
flask db-init
flask seed-data
```

### 4. Run Application
```bash
python app.py
```

Visit: `http://localhost:5000`

## 🧪 Quick Test

### Test Interface
Go to: `http://localhost:5000/test`

### Default Login Credentials
- **Owner**: owner@gym.com / owner123
- **Manager**: manager.downtown@gym.com / manager123  
- **Staff**: receptionist@gym.com / receptionist123
- **Customer**: john.customer@gym.com / customer123

### API Testing
1. Login with any account at `/test/auth`
2. Navigate to other test pages to try API endpoints
3. Each test page shows forms and responses

## 🔍 What's Included After Setup

### Sample Data
- 3 gym branches (Downtown, Uptown, Westside)
- 6 user accounts (different roles)
- 4 subscription plans
- 2 sample customers with active subscriptions
- Payment history and attendance records
- Sample complaints

### Ready-to-Use Features
- ✅ Multi-branch management
- ✅ Role-based access control  
- ✅ Customer management
- ✅ Subscription & payment tracking
- ✅ Attendance system
- ✅ Complaint management
- ✅ Dashboard analytics
- ✅ Manual testing interface

## 📋 Next Steps
1. Explore the test interface to understand all features
2. Check README.md for detailed documentation
3. Review API_DOCS.md for API specifications
4. Customize for your specific gym requirements

## 🛠️ Production Setup
For production deployment:
1. Set up PostgreSQL database
2. Configure production environment variables
3. Use production WSGI server (Gunicorn)
4. Set up reverse proxy (Nginx)

See README.md for detailed production deployment guide.