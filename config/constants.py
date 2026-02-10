"""
Constants and configuration settings for EdFast application.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file in the root directory
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(root_dir, '.env')
load_dotenv(env_path)

# API Keys and Configuration
# Read from environment variable, fail gracefully if not set
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GEMINI_MODEL_NAME = os.getenv('GEMINI_MODEL_NAME', 'gemini-2.0-flash-lite')
GROQ_MODEL_NAME = os.getenv('GROQ_MODEL_NAME', 'Llama3-8b-8192')

# File paths
USERS_FILE = 'users.json'
COURSES_FILE = 'courses.json'
CHROMADB_PATH = 'chromadb'

# Application settings
APP_TITLE = "EdFast"
APP_ICON = "🎓"
APP_LAYOUT = "wide"

# Resume settings
DEFAULT_DEGREE = "Bachelor of Science in Computer Science"
DEFAULT_INSTITUTION = "FAST University"
DEFAULT_LOCATION = "Pakistan"
DEFAULT_GRADUATION = "Expected 2024"

# Resume styles
RESUME_STYLES = {
    "professional": {
        "name": "Professional",
        "description": "Clean, corporate-friendly design with traditional layout",
        "color": "#2563EB",
        "font_size": 11,
        "spacing": "normal"
    },
    "modern": {
        "name": "Modern",
        "description": "Contemporary design with accent colors and modern typography",
        "color": "#059669",
        "font_size": 10,
        "spacing": "compact"
    },
    "creative": {
        "name": "Creative",
        "description": "Eye-catching design with unique sections and vibrant colors",
        "color": "#DC2626",
        "font_size": 10,
        "spacing": "relaxed"
    }
}

# UI Constants
MAIN_HEADER_CLASS = "main-header"
SUB_HEADER_CLASS = "sub-header"
SECTION_HEADER_CLASS = "section-header"
CARD_CLASS = "card"

# ChromaDB settings
COLLECTION_NAME = "transcript_embeddings"
CHROMADB_TIMEOUT = 10

# Token limits
MAX_CONTEXT_LENGTH = 500
MAX_COURSES_DISPLAY = 20
MAX_RECENT_COURSES = 10 