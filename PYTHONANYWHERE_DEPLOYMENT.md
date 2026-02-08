# 🚀 PythonAnywhere Deployment Guide

## 📋 Complete Guide to Deploy Gym Backend to PythonAnywhere

**Repository**: https://github.com/zyadwael2009/gym  
**PythonAnywhere URL**: https://gymclub.pythonanywhere.com

---

## 🎯 Prerequisites

1. ✅ GitHub repository ready: https://github.com/zyadwael2009/gym
2. ✅ PythonAnywhere account created
3. ✅ Flask backend code ready in `/backend` folder

---

## 📝 STEP-BY-STEP DEPLOYMENT

### **STEP 1: Create PythonAnywhere Account** (If not done)

1. Go to: https://www.pythonanywhere.com
2. Sign up for a **free account** (or use existing account)
3. Verify your email
4. Login to your dashboard

---

### **STEP 2: Open a Bash Console**

1. In PythonAnywhere dashboard, click **"Consoles"**
2. Click **"Bash"** to open a new bash console
3. You'll see a terminal window

---

### **STEP 3: Clone Your GitHub Repository**

In the bash console, run these commands:

```bash
# Navigate to home directory
cd ~

# Clone your repository
git clone https://github.com/zyadwael2009/gym.git

# Navigate to backend folder
cd gym/backend

# List files to verify
ls -la
```

You should see all your backend files (app.py, requirements.txt, etc.)

---

### **STEP 4: Create Virtual Environment**

```bash
# Create virtual environment
mkvirtualenv gym-backend --python=python3.10

# Activate it (should auto-activate after creation)
workon gym-backend

# Verify Python version
python --version
```

---

### **STEP 5: Install Dependencies**

```bash
# Make sure you're in the backend folder
cd ~/gym/backend

# Install all requirements
pip install -r requirements.txt

# Install additional packages if needed
pip install flask flask-sqlalchemy flask-jwt-extended flask-cors flask-migrate
```

---

### **STEP 6: Initialize Database**

```bash
# Run the seed script to create and populate database
python seed.py

# Verify database was created
ls -la gym_management.db
```

---

### **STEP 7: Configure Web App**

1. Go to **"Web"** tab in PythonAnywhere dashboard
2. Click **"Add a new web app"**
3. Choose your domain: **gymclub.pythonanywhere.com**
4. Select **"Manual configuration"** (not Flask wizard)
5. Choose **Python 3.10**
6. Click **Next**

---

### **STEP 8: Configure WSGI File**

1. In the **Web** tab, find **"Code"** section
2. Click on the **WSGI configuration file** link (e.g., `/var/www/gymclub_pythonanywhere_com_wsgi.py`)
3. **Delete all existing content**
4. **Paste this code**:

```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/YOUR_USERNAME/gym/backend'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set environment variables
os.environ['FLASK_APP'] = 'app.py'

# Import Flask app
from app import create_app
application = create_app()
```

**IMPORTANT**: Replace `YOUR_USERNAME` with your actual PythonAnywhere username!

5. Click **Save**

---

### **STEP 9: Configure Virtual Environment**

1. Still in the **Web** tab, find **"Virtualenv"** section
2. Enter the path to your virtual environment:
   ```
   /home/YOUR_USERNAME/.virtualenvs/gym-backend
   ```
3. Replace `YOUR_USERNAME` with your actual username

---

### **STEP 10: Configure Static Files** (Optional but recommended)

In the **Static files** section, add:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/YOUR_USERNAME/gym/backend/static` |

---

### **STEP 11: Set Working Directory**

1. In the **Web** tab, find **"Code"** section
2. Set **"Working directory"** to:
   ```
   /home/YOUR_USERNAME/gym/backend
   ```

---

### **STEP 12: Reload Web App**

1. Scroll to the top of the **Web** tab
2. Click the big green **"Reload"** button
3. Wait for it to reload (may take 30 seconds)

---

### **STEP 13: Test Your API**

1. Open a new browser tab
2. Test these endpoints:

```
✅ Health Check:
https://gymclub.pythonanywhere.com/

✅ Test Login:
https://gymclub.pythonanywhere.com/api/auth/login
Method: POST
Body: {"username": "owner", "password": "owner123"}
```

---

## 🔧 TROUBLESHOOTING

### Check Error Logs

If something doesn't work:

1. Go to **Web** tab
2. Click on **"Log files"**
3. Check:
   - **Error log**: See what went wrong
   - **Server log**: See requests
   - **Access log**: See traffic

---

### Common Issues & Fixes

#### **Issue 1: Import Error**
```
Error: No module named 'flask'
```
**Fix**:
```bash
workon gym-backend
pip install flask flask-sqlalchemy flask-jwt-extended flask-cors
```

---

#### **Issue 2: Database Not Found**
```
Error: Unable to open database file
```
**Fix**:
```bash
cd ~/gym/backend
python seed.py
```

---

#### **Issue 3: CORS Error**
**Fix**: Update `app.py` to allow all origins:
```python
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

---

#### **Issue 4: 504 Gateway Timeout**
**Fix**: Reduce timeout or optimize database queries. For free tier, keep requests under 5 seconds.

---

## 🔄 UPDATE BACKEND CODE

When you make changes to backend code:

```bash
# SSH into PythonAnywhere bash console
cd ~/gym/backend

# Pull latest changes from GitHub
git pull origin main

# If you changed dependencies:
workon gym-backend
pip install -r requirements.txt

# If database schema changed:
python seed.py

# Reload the web app
# Go to Web tab and click "Reload"
```

---

## 📱 CONNECT FLUTTER APP

Your Flutter app is already configured to use PythonAnywhere!

**API Base URL**: `https://gymclub.pythonanywhere.com/api`

### Test Credentials:
```
Owner:        owner / owner123
Manager:      manager / manager123
Receptionist: receptionist / receptionist123
Accountant:   accountant / accountant123
Customer:     customer / customer123
```

---

## 🔐 IMPORTANT SECURITY NOTES

### For Production:

1. **Change Secret Keys** in `config.py`:
```python
SECRET_KEY = 'your-super-secret-production-key'
JWT_SECRET_KEY = 'your-jwt-secret-production-key'
```

2. **Change All Passwords**:
```bash
cd ~/gym/backend
python reset_passwords.py
```

3. **Use Environment Variables**:
```bash
# In bash console:
echo "export SECRET_KEY='your-secret'" >> ~/.bashrc
echo "export JWT_SECRET_KEY='your-jwt-secret'" >> ~/.bashrc
source ~/.bashrc
```

Then update `config.py`:
```python
import os
SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-key')
```

4. **Enable HTTPS Only** (already done - PythonAnywhere provides SSL)

---

## 📊 PYTHONANYWHERE FREE TIER LIMITS

- ✅ 1 web app
- ✅ 512 MB disk space
- ✅ 100,000 requests per day
- ⚠️ App goes to sleep after inactivity
- ⚠️ No outbound HTTPS to most sites
- ⚠️ No scheduled tasks

**For unlimited**: Upgrade to paid plan ($5/month)

---

## 🎯 QUICK REFERENCE

### Bash Console Commands:
```bash
# Activate virtual environment
workon gym-backend

# Navigate to project
cd ~/gym/backend

# Update from GitHub
git pull origin main

# Install dependencies
pip install -r requirements.txt

# Reset database
python seed.py

# Check logs
tail -f /var/log/gymclub.pythonanywhere.com.error.log
```

### Important Paths:
```
Project:        /home/YOUR_USERNAME/gym/backend
Virtual Env:    /home/YOUR_USERNAME/.virtualenvs/gym-backend
WSGI File:      /var/www/gymclub_pythonanywhere_com_wsgi.py
Database:       /home/YOUR_USERNAME/gym/backend/gym_management.db
```

---

## ✅ VERIFICATION CHECKLIST

After deployment, verify:

- [ ] Web app shows as running (green dot)
- [ ] API root URL loads: https://gymclub.pythonanywhere.com/
- [ ] Login endpoint works
- [ ] Flutter app connects successfully
- [ ] All 5 test users can login
- [ ] Dashboard loads for each role
- [ ] Customer creation works
- [ ] Branch management works

---

## 📞 SUPPORT

**Developer**: زياد وائل لطفى مصطفى  
**Email**: zwaellotfy@ams-benha.com  
**Repository**: https://github.com/zyadwael2009/gym

---

## 🎉 SUCCESS!

Once deployed, your backend will be:
- ✅ Always online (24/7)
- ✅ Accessible from anywhere
- ✅ Using HTTPS (secure)
- ✅ Connected to Flutter app
- ✅ Production ready

**Next**: Test with your Flutter app! 🚀

