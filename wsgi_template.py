"""
WSGI Configuration for PythonAnywhere
======================================

Copy this content to your PythonAnywhere WSGI configuration file.
Replace YOUR_USERNAME with your actual PythonAnywhere username.

File location on PythonAnywhere:
/var/www/gymclub_pythonanywhere_com_wsgi.py
"""

import sys
import os

# ============================================
# IMPORTANT: Replace YOUR_USERNAME below
# ============================================
project_home = '/home/YOUR_USERNAME/gym/backend'

# Add your project directory to the sys.path
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set environment variables
os.environ['FLASK_APP'] = 'app.py'
os.environ['FLASK_ENV'] = 'production'

# Import Flask app
from app import create_app

# Create the application instance
application = create_app()

# For debugging (remove in production)
# print("Python version:", sys.version)
# print("Python path:", sys.path)
# print("Application loaded successfully!")

