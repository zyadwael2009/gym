# ⚡ QUICK SETUP - PythonAnywhere in 5 Minutes

## 🎯 Your Backend URL
**https://gymclub.pythonanywhere.com**

## ✅ Flutter App Already Configured!
Your Flutter app is now pointing to PythonAnywhere. No changes needed!

---

## 📋 5-MINUTE SETUP

### **STEP 1: Open PythonAnywhere Bash**
1. Login to: https://www.pythonanywhere.com
2. Click **"Consoles"** → **"Bash"**

### **STEP 2: Run Setup Commands**
Copy and paste these commands **one by one**:

```bash
# Clone repository
cd ~
git clone https://github.com/zyadwael2009/gym.git
cd gym/backend

# Create virtual environment
mkvirtualenv gym-backend --python=python3.10

# Install dependencies
pip install -r requirements.txt

# Initialize database with test data
python seed.py
```

### **STEP 3: Create Web App**
1. Click **"Web"** tab
2. Click **"Add a new web app"**
3. Domain: **gymclub.pythonanywhere.com**
4. Select: **"Manual configuration"**
5. Python version: **3.10**

### **STEP 4: Configure WSGI**
1. In Web tab, click on **WSGI configuration file** link
2. **Delete everything** in the file
3. **Paste this** (replace YOUR_USERNAME with your username):

```python
import sys
import os

project_home = '/home/YOUR_USERNAME/gym/backend'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

os.environ['FLASK_APP'] = 'app.py'

from app import create_app
application = create_app()
```

4. Click **Save**

### **STEP 5: Set Virtual Environment**
1. In Web tab, find **"Virtualenv"** section
2. Enter path:
```
/home/YOUR_USERNAME/.virtualenvs/gym-backend
```

### **STEP 6: Set Working Directory**
1. In Web tab, find **"Code"** section
2. Set **Working directory** to:
```
/home/YOUR_USERNAME/gym/backend
```

### **STEP 7: Reload**
1. Scroll to top of Web tab
2. Click big green **"Reload"** button
3. Wait 30 seconds

### **STEP 8: Test**
Open in browser:
```
https://gymclub.pythonanywhere.com/
```

You should see: `"Gym Management API is running!"`

---

## ✅ TEST CREDENTIALS

Login with these users:

| Role | Username | Password |
|------|----------|----------|
| 👑 Owner | owner | owner123 |
| 🏢 Manager | manager | manager123 |
| 🎫 Receptionist | receptionist | receptionist123 |
| 💰 Accountant | accountant | accountant123 |
| 🏋️ Customer | customer | customer123 |

---

## 🔧 TROUBLESHOOTING

### If you see an error:
1. Go to **Web** tab
2. Click **"Log files"**
3. Check **Error log**

### Common fixes:

**Error: No module named 'flask'**
```bash
workon gym-backend
pip install -r requirements.txt
```

**Error: Database not found**
```bash
cd ~/gym/backend
python seed.py
```

---

## 🔄 UPDATE CODE

When you update GitHub repository:

```bash
# In PythonAnywhere bash console:
cd ~/gym/backend
git pull origin main
# Then reload web app in Web tab
```

---

## 📱 FLUTTER APP CONNECTION

Your Flutter app is configured to use:
```
https://gymclub.pythonanywhere.com/api
```

Just rebuild and run your app:
```bash
cd D:\Programming\Flutter\gym\frontend\gym_app
flutter run
```

---

## ✨ DONE!

Your backend is now:
- ✅ Running 24/7 online
- ✅ Using HTTPS (secure)
- ✅ Accessible from anywhere
- ✅ Connected to Flutter app

**Test it**: Login with owner/owner123 in your Flutter app! 🚀

