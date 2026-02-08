# 🔧 URGENT FIX - WSGI Import Error

## ❌ The Problem

**Error**: `ImportError: cannot import name 'create_app' from 'app'`

**Why**: There's a naming conflict:
- `app.py` (file) - contains `create_app()` function
- `app/` (folder) - package with models and API
- Python imports from `app/` folder instead of `app.py` file!

---

## ✅ THE SOLUTION

Use this **CORRECTED WSGI configuration**:

### Step 1: Go to PythonAnywhere Web Tab

1. Click on your WSGI configuration file link
2. **DELETE EVERYTHING** in the file
3. **PASTE THIS**:

```python
import sys
import os
import importlib.util

# Project path
project_home = '/home/gymclub/gym'

# Add to Python path
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set environment
os.environ['FLASK_APP'] = 'app.py'
os.environ['FLASK_ENV'] = 'production'

# Load app.py directly (avoids app/ folder conflict)
app_py_path = os.path.join(project_home, 'app.py')
spec = importlib.util.spec_from_file_location("app_main", app_py_path)
app_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_main)

# Create Flask application
application = app_main.create_app()
```

4. Click **"Save"**

### Step 2: Reload Web App

1. Scroll to top of Web tab
2. Click green **"Reload"** button
3. Wait 30 seconds

### Step 3: Test

Open: https://gymclub.pythonanywhere.com/

**Should see**: "Gym Management API is running!" ✅

---

## 🎯 Quick Copy-Paste Version

If you need to copy-paste via bash:

```bash
# Download the correct WSGI file
cd ~/gym
cat > /var/www/gymclub_pythonanywhere_com_wsgi.py << 'EOF'
import sys
import os
import importlib.util

project_home = '/home/gymclub/gym'

if project_home not in sys.path:
    sys.path = [project_home] + sys.path

os.environ['FLASK_APP'] = 'app.py'
os.environ['FLASK_ENV'] = 'production'

app_py_path = os.path.join(project_home, 'app.py')
spec = importlib.util.spec_from_file_location("app_main", app_py_path)
app_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_main)

application = app_main.create_app()
EOF

# Reload web app (or use Web tab button)
touch /var/www/gymclub_pythonanywhere_com_wsgi.py
```

---

## 📋 Verification

After reloading, check:

1. **No errors in Error Log**: Web tab → Log files → Error log
2. **API responds**: https://gymclub.pythonanywhere.com/
3. **Login works**: Test with owner/owner123
4. **Flutter app connects**: Should work now!

---

## 🔍 Why This Works

```python
# ❌ Old way (doesn't work):
from app import create_app  # Imports from app/ folder

# ✅ New way (works):
import importlib.util
spec = importlib.util.spec_from_file_location("app_main", "app.py")
app_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_main)
application = app_main.create_app()  # Gets from app.py file
```

---

**Status**: Copy the WSGI code above and reload your web app! 🚀

