"""
EdFast Flask API - Main Application
RESTful API for EdFast academic management platform
"""

import os
import sys
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.app_config import USE_DATABASE
from database.db_config import init_database

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'edfast-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['REQUEST_TIMEOUT'] = 120  # 120 seconds timeout for long-running operations

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions
# Allow both localhost (development) and dev tunnel domains
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000", 
            "http://localhost:3001",
            "https://x7mq0j1w-3000.asse.devtunnels.ms",
            "http://x7mq0j1w-3000.asse.devtunnels.ms"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"],
        "expose_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "max_age": 3600
    }
})

jwt = JWTManager(app)

# Initialize database
if USE_DATABASE:
    try:
        db_config = init_database(create_tables=True)
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"⚠ Database initialization error: {e}")

# Import and register blueprints
from api.auth import auth_bp
from api.users import users_bp
from api.peerhub import peerhub_bp
from api.chatbot import chatbot_bp
from api.timetable import timetable_bp
from api.resume import resume_bp
from api.courses import courses_bp
from api.dashboard import dashboard_bp
from api.linkedin import linkedin_bp

app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
app.register_blueprint(users_bp, url_prefix='/api/v1/users')
app.register_blueprint(peerhub_bp, url_prefix='/api/v1/peerhub')
app.register_blueprint(chatbot_bp, url_prefix='/api/v1/chatbot')
app.register_blueprint(timetable_bp, url_prefix='/api/v1/timetable')
app.register_blueprint(resume_bp, url_prefix='/api/v1/resume')
app.register_blueprint(courses_bp, url_prefix='/api/v1/courses')
app.register_blueprint(dashboard_bp, url_prefix='/api/v1/dashboard')
app.register_blueprint(linkedin_bp, url_prefix='/api/v1/linkedin')


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Resource not found',
        'message': str(error)
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': str(error)
    }), 500


@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        'success': False,
        'error': 'File too large',
        'message': 'Maximum file size is 16MB'
    }), 413


# JWT error handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'success': False,
        'error': 'Token expired',
        'message': 'The token has expired. Please login again.'
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'success': False,
        'error': 'Invalid token',
        'message': 'Token verification failed.'
    }), 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'success': False,
        'error': 'Authorization required',
        'message': 'Access token is missing.'
    }), 401


# Health check endpoint
@app.route('/api/v1/health', methods=['GET'])
def health_check():
    return jsonify({
        'success': True,
        'message': 'EdFast API is running',
        'version': '1.0.0',
        'database': 'connected' if USE_DATABASE else 'json_files'
    }), 200


# API documentation endpoint
@app.route('/api/v1', methods=['GET'])
def api_info():
    return jsonify({
        'success': True,
        'message': 'EdFast API v1',
        'documentation': '/api/v1/docs',
        'endpoints': {
            'auth': '/api/v1/auth',
            'users': '/api/v1/users',
            'peerhub': '/api/v1/peerhub',
            'chatbot': '/api/v1/chatbot',
            'timetable': '/api/v1/timetable',
            'resume': '/api/v1/resume',
            'courses': '/api/v1/courses',
            'linkedin': '/api/v1/linkedin'
        }
    }), 200


if __name__ == '__main__':
    # Development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )


