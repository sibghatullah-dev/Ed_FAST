"""
Users API Endpoints
Handles user profile, transcript, and resume management
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from auth import (
    get_user_name, get_user_description, update_user_description,
    get_user_transcript, update_user_transcript,
    get_user_resume_data, update_user_resume_data, UserService
)
from data.transcript_processing import extract_transcript_with_gemini, initialize_gemini_api

users_bp = Blueprint('users', __name__)

# Initialize Gemini API
initialize_gemini_api()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@users_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user profile"""
    try:
        username = get_jwt_identity()
        name = get_user_name(username)
        description = get_user_description(username)
        transcript_file = get_user_transcript(username)
        
        # Get transcript data if available
        transcript_data = None
        try:
            from auth.db_user_service import UserService
            transcript_data = UserService.get_user_transcript_data(username)
        except:
            pass
        
        return jsonify({
            'success': True,
            'data': {
                'username': username,
                'name': name,
                'description': description,
                'transcript_file': transcript_file,
                'has_transcript': bool(transcript_file),
                'transcript_data': transcript_data
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get user profile',
            'message': str(e)
        }), 500


@users_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_current_user():
    """
    Update current user profile
    
    Request Body:
    {
        "name": "New Name" (optional),
        "description": "New description" (optional)
    }
    """
    try:
        username = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Update description if provided
        if 'description' in data:
            update_user_description(username, data['description'])
        
        # Update name if provided (requires UserService)
        if 'name' in data:
            try:
                from auth.db_user_service import UserService
                UserService.update_user_profile(username, name=data['name'])
            except:
                pass
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to update profile',
            'message': str(e)
        }), 500


@users_bp.route('/me/transcript', methods=['GET'])
@jwt_required()
def get_transcript():
    """Get user transcript data"""
    try:
        username = get_jwt_identity()
        transcript_file = get_user_transcript(username)
        
        # Get transcript data
        transcript_data = None
        try:
            from auth.db_user_service import UserService
            transcript_data = UserService.get_user_transcript_data(username)
        except:
            pass
        
        return jsonify({
            'success': True,
            'data': {
                'transcript_file': transcript_file,
                'transcript_data': transcript_data,
                'has_transcript': bool(transcript_file)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get transcript',
            'message': str(e)
        }), 500


@users_bp.route('/me/transcript', methods=['POST'])
@jwt_required()
def upload_transcript():
    """
    Upload and process transcript image
    
    Form Data:
        file: Image file (png, jpg, jpeg, gif, pdf)
    """
    try:
        username = get_jwt_identity()
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif, pdf'
            }), 400
        
        # Save file
        filename = secure_filename(f"{username}_transcript_{file.filename}")
        upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'transcripts')
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # Process transcript with Gemini AI
        from PIL import Image
        image = Image.open(filepath)
        transcript_data = extract_transcript_with_gemini(image)
        
        if transcript_data:
            # Update user transcript
            update_user_transcript(username, filepath)
            
            # Update transcript data if using database
            try:
                from auth.db_user_service import UserService
                UserService.update_user_transcript(username, filepath, transcript_data)
            except:
                pass
            
            return jsonify({
                'success': True,
                'message': 'Transcript uploaded and processed successfully',
                'data': {
                    'transcript_file': filepath,
                    'transcript_data': transcript_data
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to process transcript image'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to upload transcript',
            'message': str(e)
        }), 500


@users_bp.route('/me/description', methods=['GET'])
@jwt_required()
def get_description():
    """Get user description"""
    try:
        username = get_jwt_identity()
        description = get_user_description(username)
        
        return jsonify({
            'success': True,
            'data': {
                'description': description
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get description',
            'message': str(e)
        }), 500


@users_bp.route('/me/description', methods=['PUT'])
@jwt_required()
def update_description():
    """
    Update user description
    
    Request Body:
    {
        "description": "My description..."
    }
    """
    try:
        username = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'description' not in data:
            return jsonify({
                'success': False,
                'error': 'Description is required'
            }), 400
        
        update_user_description(username, data['description'])
        
        return jsonify({
            'success': True,
            'message': 'Description updated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to update description',
            'message': str(e)
        }), 500


@users_bp.route('/me/resume', methods=['GET'])
@jwt_required()
def get_resume():
    """Get user resume data"""
    try:
        username = get_jwt_identity()
        resume_data = get_user_resume_data(username)
        
        return jsonify({
            'success': True,
            'data': {
                'resume_data': resume_data
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get resume data',
            'message': str(e)
        }), 500


@users_bp.route('/me/resume', methods=['PUT'])
@jwt_required()
def update_resume():
    """
    Update user resume data
    
    Request Body:
    {
        "resume_data": { ... resume fields ... }
    }
    """
    try:
        username = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'resume_data' not in data:
            return jsonify({
                'success': False,
                'error': 'Resume data is required'
            }), 400
        
        update_user_resume_data(username, data['resume_data'])
        
        return jsonify({
            'success': True,
            'message': 'Resume data updated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to update resume data',
            'message': str(e)
        }), 500


