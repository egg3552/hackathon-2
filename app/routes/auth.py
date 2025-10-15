"""
Authentication routes for user registration, login, and logout.
"""
from flask import (
    Blueprint, request, jsonify, render_template, redirect, url_for
)
from flask_login import login_user, logout_user, current_user
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET'])
def login_page():
    """Render login page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return render_template('login.html')


@auth_bp.route('/api/login', methods=['POST'])
def login():
    """
    User login endpoint.
    
    Expected JSON:
        {
            "username": "user1",
            "password": "password123"
        }
    
    Returns:
        JSON response with user data or error message
    """
    if current_user.is_authenticated:
        return jsonify({
            'message': 'Already logged in',
            'user': current_user.to_dict()
        }), 200
    
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if user is None or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    login_user(user, remember=True)
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict()
    }), 200


@auth_bp.route('/api/register', methods=['POST'])
def register():
    """
    User registration endpoint.
    
    Expected JSON:
        {
            "username": "newuser",
            "email": "user@example.com",
            "password": "password123"
        }
    
    Returns:
        JSON response with new user data or error message
    """
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('username') or not data.get('email') \
            or not data.get('password'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create new user
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        
        # Auto-login after registration
        login_user(user, remember=True)
        
        return jsonify({
            'message': 'Registration successful',
            'user': user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Registration failed',
            'details': str(e)
        }), 500


@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    """
    User logout endpoint.
    
    Returns:
        JSON response confirming logout
    """
    logout_user()
    return jsonify({'message': 'Logout successful'}), 200


@auth_bp.route('/api/current-user', methods=['GET'])
def current_user_info():
    """
    Get current logged-in user information.
    
    Returns:
        JSON response with user data or null if not authenticated
    """
    if current_user.is_authenticated:
        return jsonify({'user': current_user.to_dict()}), 200
    return jsonify({'user': None}), 200
