"""
Chatbot module for EdFast application.
Handles LLM initialization and chat functionality.
"""

import os
import logging
import time
from datetime import datetime, timedelta
from langchain_google_genai import ChatGoogleGenerativeAI
from config.constants import GEMINI_API_KEY, GEMINI_MODEL_NAME
from chat.context_optimizer import create_optimized_context, get_relevant_course_info, create_optimized_prompt

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Rate limiting configuration
RATE_LIMIT_CONFIG = {
    'requests_per_minute': 5,  # Max 5 requests per minute per user
    'requests_per_hour': 30,   # Max 30 requests per hour per user
    'user_requests': {}  # Track user requests
}


def check_rate_limit(username: str) -> tuple[bool, str]:
    """Check if user has exceeded rate limits."""
    now = datetime.now()
    
    if username not in RATE_LIMIT_CONFIG['user_requests']:
        RATE_LIMIT_CONFIG['user_requests'][username] = []
    
    user_requests = RATE_LIMIT_CONFIG['user_requests'][username]
    
    # Remove old requests (older than 1 hour)
    user_requests[:] = [req_time for req_time in user_requests if now - req_time < timedelta(hours=1)]
    
    # Check hour limit
    if len(user_requests) >= RATE_LIMIT_CONFIG['requests_per_hour']:
        return False, f"You've reached the hourly limit ({RATE_LIMIT_CONFIG['requests_per_hour']} requests/hour). Please try again later."
    
    # Check minute limit
    recent_requests = [req_time for req_time in user_requests if now - req_time < timedelta(minutes=1)]
    if len(recent_requests) >= RATE_LIMIT_CONFIG['requests_per_minute']:
        wait_time = int((recent_requests[0] + timedelta(minutes=1) - now).total_seconds()) + 1
        return False, f"Please slow down. You can make another request in {wait_time} seconds."
    
    # Add current request
    user_requests.append(now)
    return True, "OK"


def init_llm():
    """Initialize the LLM (Large Language Model) for chatbot functionality using Gemini."""
    try:
        # Log configuration
        logger.info(f"Initializing Gemini LLM with model: {GEMINI_MODEL_NAME}")
        logger.info(f"API Key present: {bool(GEMINI_API_KEY)}")
        logger.info(f"API Key length: {len(GEMINI_API_KEY) if GEMINI_API_KEY else 0}")
        
        if not GEMINI_API_KEY:
            logger.error("❌ Gemini API key is not set. Please check:")
            logger.error("   1. .env file exists in root directory")
            logger.error("   2. .env contains: GEMINI_API_KEY=<your-key>")
            logger.error("   3. Backend was restarted after creating .env file")
            return None
        
        logger.info("Creating ChatGoogleGenerativeAI instance...")
        llm = ChatGoogleGenerativeAI(
            google_api_key=GEMINI_API_KEY, 
            model=GEMINI_MODEL_NAME,
            temperature=0.7,
            max_output_tokens=1024,  # Reduced from 2048 to conserve tokens
            timeout=60,  # Reduced from 120 to 60 seconds
            max_retries=2  # Reduced from 3 to 2
        )
        
        logger.info("Testing LLM with simple prompt...")
        # Test the LLM with a simple prompt
        test_response = llm.invoke("Hello")
        if test_response:
            logger.info("✅ Successfully initialized LLM with Gemini")
            return llm
        else:
            logger.error("❌ LLM initialization test failed - no response")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error initializing Gemini LLM: {str(e)}")
        
        # Check for quota errors
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            logger.error("⚠️ API QUOTA EXHAUSTED!")
            logger.error("Solutions:")
            logger.error("1. Enable billing: https://ai.google.dev/ → Enable billing")
            logger.error("2. Wait for quota to reset")
            logger.error("3. Use a different API key")
        
        logger.error("Troubleshooting:")
        logger.error(f"  - Check GEMINI_API_KEY is valid")
        logger.error(f"  - Check internet connection")
        logger.error(f"  - Check API key has proper permissions")
        logger.error(f"  - Error details: {type(e).__name__}: {str(e)}")
        return None


def process_chat_query(llm, user_input, transcript_data, user_description, courses_data):
    """Process a chat query and return the response."""
    try:
        # Validate inputs
        if not llm:
            logger.error("LLM is not initialized")
            return "I'm sorry, but the AI service is not available. Please try again later."
        
        if not user_input or not user_input.strip():
            return "Please enter a valid question."
        
        logger.info(f"Processing chat query: {user_input[:50]}...")
        
        # Create optimized context based on the user's question
        optimized_context = create_optimized_context(transcript_data, user_description, user_input)
        
        # Get relevant course information only if needed
        course_info = get_relevant_course_info(courses_data, user_input)
        
        # Create optimized prompt
        prompt = create_optimized_prompt(optimized_context, course_info, user_input)
        
        logger.info("Sending request to Gemini API...")
        # Query LLM
        response = llm.invoke(prompt)
        logger.info("✅ Successfully received response from Gemini")
        return response.content
        
    except Exception as e:
        # Log the error for debugging
        logger.error(f"❌ Chatbot error: {type(e).__name__}: {str(e)}")
        
        # Check for quota errors
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            logger.error("⚠️ API QUOTA EXHAUSTED!")
            error_msg = "API quota exceeded. Please enable billing or try again later."
            logger.error(f"Message: {error_msg}")
            return error_msg
        
        logger.error(f"Error details: {str(e)}")
        return "I'm sorry, I encountered an error while processing your question. Please try rephrasing your question or try again later."


def add_to_chat_history(chat_history, role, content):
    """Add a message to the chat history."""
    chat_history.append({"role": role, "content": content}) 