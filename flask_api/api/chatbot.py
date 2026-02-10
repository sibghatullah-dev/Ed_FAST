"""
Chatbot API Endpoints
Handles AI-powered academic chatbot conversations
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from chat.chatbot import init_llm, process_chat_query, check_rate_limit
from chat.context_optimizer import create_optimized_context
from auth import get_user_description, UserService
from config.constants import GEMINI_API_KEY
import json

chatbot_bp = Blueprint('chatbot', __name__)

# In-memory chat history storage (should be moved to database in production)
chat_histories = {}

# Debug endpoint to check if API key is loaded
@chatbot_bp.route('/debug/status', methods=['GET'])
def debug_status():
    """Debug endpoint to check chatbot configuration"""
    try:
        return jsonify({
            'success': True,
            'status': 'API Key Loaded' if GEMINI_API_KEY else 'API Key NOT Found',
            'gemini_api_key_present': bool(GEMINI_API_KEY),
            'api_key_length': len(GEMINI_API_KEY) if GEMINI_API_KEY else 0,
            'message': 'Chatbot is ready' if GEMINI_API_KEY else 'Missing GEMINI_API_KEY in .env file'
        }), 200
    except Exception as e:
        logger.error(f"Debug status error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@chatbot_bp.route('/query', methods=['POST'])
@jwt_required()
def chat_query():
    """
    Send a chat query to the AI academic advisor
    
    Request Body:
    {
        "message": "Your question to the AI"
    }
    """
    try:
        username = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        user_input = data['message'].strip()
        
        if not user_input:
            return jsonify({
                'success': False,
                'error': 'Message cannot be empty'
            }), 400
        
        # Check rate limit
        is_allowed, rate_limit_msg = check_rate_limit(username)
        if not is_allowed:
            logger.warning(f"Rate limit exceeded for user {username}: {rate_limit_msg}")
            return jsonify({
                'success': False,
                'error': rate_limit_msg
            }), 429
        
        # Check if API key is configured
        if not GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY is not configured")
            return jsonify({
                'success': False,
                'error': 'Chatbot service is not configured. Missing GEMINI_API_KEY in environment variables.',
                'details': 'Please ensure .env file contains GEMINI_API_KEY'
            }), 503
        
        # Get user transcript data
        transcript_data = None
        try:
            from auth.db_user_service import UserService
            transcript_data = UserService.get_user_transcript_data(username)
        except Exception as e:
            logger.warning(f"Could not load transcript data: {str(e)}")
            pass
        
        # Get user description
        user_description = get_user_description(username)
        
        # Load courses data
        courses_data = None
        try:
            courses_file = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'courses.json'
            )
            with open(courses_file, 'r') as f:
                courses_data = json.load(f)
        except Exception as e:
            logger.warning(f"Could not load courses data: {str(e)}")
            pass
        
        # Initialize LLM if not already initialized
        logger.info(f"Initializing LLM for user: {username}")
        llm = init_llm()
        
        if not llm:
            logger.error("Failed to initialize LLM")
            return jsonify({
                'success': False,
                'error': 'AI service is not available. Check your API key configuration.'
            }), 503
        
        logger.info(f"Processing chat query from {username}")
        # Process chat query
        response = process_chat_query(
            llm,
            user_input,
            transcript_data,
            user_description,
            courses_data
        )
        
        # Store chat history
        if username not in chat_histories:
            chat_histories[username] = []
        
        chat_histories[username].append({
            'role': 'user',
            'content': user_input,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        })
        
        chat_histories[username].append({
            'role': 'assistant',
            'content': response,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        })
        
        # Keep only last 20 messages
        if len(chat_histories[username]) > 20:
            chat_histories[username] = chat_histories[username][-20:]
        
        return jsonify({
            'success': True,
            'data': {
                'message': response,
                'user_input': user_input
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to process query',
            'message': str(e)
        }), 500


@chatbot_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    """Get chat history for current user"""
    try:
        username = get_jwt_identity()
        
        history = chat_histories.get(username, [])
        
        return jsonify({
            'success': True,
            'data': {
                'history': history,
                'count': len(history)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get chat history',
            'message': str(e)
        }), 500


@chatbot_bp.route('/history', methods=['DELETE'])
@jwt_required()
def clear_history():
    """Clear chat history for current user"""
    try:
        username = get_jwt_identity()
        
        if username in chat_histories:
            chat_histories[username] = []
        
        return jsonify({
            'success': True,
            'message': 'Chat history cleared successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to clear chat history',
            'message': str(e)
        }), 500


