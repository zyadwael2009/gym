#!/bin/bash

# ====================================================
# PythonAnywhere Quick Setup Script
# ====================================================
# Run this script in PythonAnywhere bash console
# to quickly set up the backend
# ====================================================

echo "=========================================="
echo "  GYM BACKEND - PYTHONANYWHERE SETUP"
echo "=========================================="
echo ""

# Step 1: Clone repository
echo "Step 1: Cloning repository..."
cd ~
if [ -d "gym" ]; then
    echo "Repository already exists. Pulling latest changes..."
    cd gym
    git pull origin main
    cd ~
else
    git clone https://github.com/zyadwael2009/gym.git
fi

# Step 2: Create virtual environment
echo ""
echo "Step 2: Creating virtual environment..."
mkvirtualenv gym-backend --python=python3.10

# Step 3: Install dependencies
echo ""
echo "Step 3: Installing dependencies..."
cd ~/gym/backend
pip install -r requirements.txt

# Step 4: Initialize database
echo ""
echo "Step 4: Initializing database..."
python seed.py

# Step 5: Verify installation
echo ""
echo "Step 5: Verifying installation..."
echo "Python version:"
python --version
echo ""
echo "Installed packages:"
pip list | grep -i flask

# Done
echo ""
echo "=========================================="
echo "  SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Go to Web tab in PythonAnywhere"
echo "2. Create a new web app"
echo "3. Configure WSGI file (use wsgi_template.py)"
echo "4. Set virtualenv path: ~/.virtualenvs/gym-backend"
echo "5. Reload the web app"
echo ""
echo "Test credentials:"
echo "  Owner: owner / owner123"
echo "  Manager: manager / manager123"
echo "  Receptionist: receptionist / receptionist123"
echo "  Accountant: accountant / accountant123"
echo "  Customer: customer / customer123"
echo ""
echo "API will be available at:"
echo "  https://gymclub.pythonanywhere.com"
echo ""

