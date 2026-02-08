"""Test pages blueprint for manual API testing"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests
import json
from datetime import date

test_bp = Blueprint('test_pages', __name__, template_folder='templates')

# Base URL for API calls (adjust as needed)
API_BASE_URL = 'http://localhost:5000/api'

@test_bp.route('/')
def index():
    """Test pages home"""
    return render_template('test_home.html')

@test_bp.route('/login', methods=['GET', 'POST'])
def test_login():
    """Login test page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            response = requests.post(f'{API_BASE_URL}/auth/login', 
                                   json={'username': username, 'password': password})
            
            if response.status_code == 200:
                data = response.json()
                session['access_token'] = data['access_token']
                session['user'] = data['user']
                flash('Login successful!', 'success')
                return redirect(url_for('test_pages.dashboard'))
            else:
                error = response.json().get('error', 'Login failed')
                flash(f'Login failed: {error}', 'error')
        
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    return render_template('login.html')

@test_bp.route('/dashboard')
def dashboard():
    """Test dashboard"""
    if 'access_token' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('test_pages.test_login'))
    
    user = session.get('user', {})
    return render_template('dashboard.html', user=user)

@test_bp.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('test_pages.test_login'))

@test_bp.route('/customers')
def customers():
    """Customer management test page"""
    if 'access_token' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('test_pages.test_login'))
    
    return render_template('customers.html')

@test_bp.route('/customers/create', methods=['POST'])
def create_customer():
    """Create customer via API"""
    if 'access_token' not in session:
        return redirect(url_for('test_pages.test_login'))
    
    try:
        # Get form data
        customer_data = {
            'username': request.form.get('username'),
            'email': request.form.get('email'),
            'password': request.form.get('password'),
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'branch_id': int(request.form.get('branch_id')),
            'phone': request.form.get('phone'),
            'date_of_birth': request.form.get('date_of_birth'),
            'gender': request.form.get('gender'),
            'emergency_contact_name': request.form.get('emergency_contact_name'),
            'emergency_contact_phone': request.form.get('emergency_contact_phone'),
            'height_cm': float(request.form.get('height_cm')) if request.form.get('height_cm') else None,
            'weight_kg': float(request.form.get('weight_kg')) if request.form.get('weight_kg') else None,
            'medical_conditions': request.form.get('medical_conditions'),
            'fitness_goals': request.form.get('fitness_goals')
        }
        
        headers = {'Authorization': f"Bearer {session['access_token']}"}
        response = requests.post(f'{API_BASE_URL}/customers/', 
                               json=customer_data, headers=headers)
        
        if response.status_code == 201:
            flash('Customer created successfully!', 'success')
        else:
            error_data = response.json()
            flash(f'Error: {error_data.get("error", "Failed to create customer")}', 'error')
    
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('test_pages.customers'))

@test_bp.route('/customers/list')
def list_customers():
    """List customers via API"""
    if 'access_token' not in session:
        return redirect(url_for('test_pages.test_login'))
    
    try:
        headers = {'Authorization': f"Bearer {session['access_token']}"}
        response = requests.get(f'{API_BASE_URL}/customers/', headers=headers)
        
        if response.status_code == 200:
            customers = response.json().get('customers', [])
            return render_template('customer_list.html', customers=customers)
        else:
            flash('Failed to load customers', 'error')
            return redirect(url_for('test_pages.customers'))
    
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('test_pages.customers'))
