"""
Authentication API Endpoints
Handles user registration, login, and token management
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from auth import user_exists, validate_login, add_user, get_user_name, UserService

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    
    Request Body:
    {
        "name": "John Doe",
        "username": "johndoe",
        "password": "password123",
        "email": "john@example.com" (optional)
    }
    """
    try:
        data = request.get_json()
        
        # Validation
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        name = data.get('name', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        email = data.get('email', '').strip()
        
        # Validate required fields
        if not name:
            return jsonify({
                'success': False,
                'error': 'Name is required'
            }), 400
        
        if not username:
            return jsonify({
                'success': False,
                'error': 'Username is required'
            }), 400
        
        if not password:
            return jsonify({
                'success': False,
                'error': 'Password is required'
            }), 400
        
        if len(password) < 6:
            return jsonify({
                'success': False,
                'error': 'Password must be at least 6 characters'
            }), 400
        
        # Check if user exists
        if user_exists(username):
            return jsonify({
                'success': False,
                'error': 'Username already exists'
            }), 409
        
        # Create user
        success = add_user(name, username, password)
        
        if success:
            # Create tokens
            access_token = create_access_token(identity=username)
            refresh_token = create_refresh_token(identity=username)
            
            return jsonify({
                'success': True,
                'message': 'User registered successfully',
                'data': {
                    'username': username,
                    'name': name,
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create user'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Registration failed',
            'message': str(e)
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login
    
    Request Body:
    {
        "username": "johndoe",
        "password": "password123"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'error': 'Username and password are required'
            }), 400
        
        # Validate credentials
        if validate_login(username, password):
            # Create tokens
            access_token = create_access_token(identity=username)
            refresh_token = create_refresh_token(identity=username)
            
            user_name = get_user_name(username)
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'data': {
                    'username': username,
                    'name': user_name,
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid username or password'
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Login failed',
            'message': str(e)
        }), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token using refresh token
    
    Headers:
        Authorization: Bearer <refresh_token>
    """
    try:
        username = get_jwt_identity()
        access_token = create_access_token(identity=username)
        
        return jsonify({
            'success': True,
            'data': {
                'access_token': access_token
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Token refresh failed',
            'message': str(e)
        }), 500


@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify():
    """
    Verify if token is valid
    
    Headers:
        Authorization: Bearer <access_token>
    """
    try:
        username = get_jwt_identity()
        user_name = get_user_name(username)
        
        return jsonify({
            'success': True,
            'data': {
                'username': username,
                'name': user_name,
                'authenticated': True
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Token verification failed',
            'message': str(e)
        }), 401


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout user (client should delete token)
    
    Headers:
        Authorization: Bearer <access_token>
    """
    return jsonify({
        'success': True,
        'message': 'Logout successful'
    }), 200




