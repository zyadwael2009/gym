# 🔧 CORRECTED PYTHONANYWHERE SETUP

## ⚠️ IMPORTANT: Repository Structure Fix

The backend files are in the **root** of the repository, not in a `/backend` folder!

---

## ✅ CORRECT SETUP COMMANDS

In PythonAnywhere bash console:

```bash
# Navigate to the gym folder (already cloned)
cd ~/gym

# Activate virtual environment (already created)
workon gym-backend

# Install dependencies
pip install -r requirements.txt

# Run seed script
python seed.py
```

---

## 📝 CORRECT WSGI CONFIGURATION

1. Go to **Web** tab
2. Click **"Add a new web app"**
3. Domain: **gymclub.pythonanywhere.com**
4. **Manual configuration**
5. Python **3.10**

### WSGI File Configuration:

Click on the WSGI configuration file and **paste this**:

```python
import sys
import os

# IMPORTANT: No /backend subfolder!
project_home = '/home/gymclub/gym'

if project_home not in sys.path:
    sys.path = [project_home] + sys.path

os.environ['FLASK_APP'] = 'app.py'

from app import create_app
application = create_app()
```

---

## 📂 CORRECT PATHS

### Virtual Environment:
```
/home/gymclub/.virtualenvs/gym-backend
```

### Working Directory:
```
/home/gymclub/gym
```

### Source Code:
```
/home/gymclub/gym
```

---

## 🚀 COMPLETE SETUP NOW

Since you already have:
- ✅ Repository cloned to `~/gym`
- ✅ Virtual environment created
- ✅ Dependencies installed (in progress)

Just do:

```bash
# Make sure you're in the right directory
cd ~/gym

# Activate virtual environment
workon gym-backend

# Finish installing if needed
pip install -r requirements.txt

# Run seed script
python seed.py
```

Then configure the web app with the paths above!

---

## 🔍 VERIFY PATHS

```bash
# Check where you are
pwd
# Should show: /home/gymclub/gym

# Check files exist
ls app.py
# Should show: app.py

# Check app folder
ls app/
# Should show: __init__.py, api/, models/, etc.
```

---

## ⚡ AFTER SETUP

1. **Configure WSGI** (use corrected path above)
2. **Set virtualenv**: `/home/gymclub/.virtualenvs/gym-backend`
3. **Set working directory**: `/home/gymclub/gym`
4. **Reload** web app
5. **Test**: https://gymclub.pythonanywhere.com/

---

**Status**: Files are in `/home/gymclub/gym` (not `/home/gymclub/gym/backend`)

