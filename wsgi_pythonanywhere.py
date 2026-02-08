"""
CORRECTED WSGI Configuration for PythonAnywhere
================================================

This version handles the naming conflict between app.py (file) and app/ (package)

Copy this to: /var/www/gymclub_pythonanywhere_com_wsgi.py
Replace gymclub with your PythonAnywhere username if different
"""

import sys
import os
import importlib.util

# ============================================
# Project path (NO /backend subfolder!)
# ============================================
project_home = '/home/gymclub/gym'

# Add project directory to Python path
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set environment variables
os.environ['FLASK_APP'] = 'app.py'
os.environ['FLASK_ENV'] = 'production'

# ============================================
# FIX: Import app.py module directly
# ============================================
# Problem: Python tries to import from app/ folder instead of app.py file
# Solution: Load app.py explicitly using importlib

app_py_path = os.path.join(project_home, 'app.py')
spec = importlib.util.spec_from_file_location("app_main", app_py_path)
app_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_main)

# Create Flask application
application = app_main.create_app()

# Debug info (uncomment if needed)
# print("✅ WSGI loaded successfully!")
# print(f"Project: {project_home}")
# print(f"Python: {sys.version}")

