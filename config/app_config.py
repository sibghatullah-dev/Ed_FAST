"""
Application Configuration
Centralized configuration for switching between JSON and Database storage.
"""

import os

# Storage backend configuration
USE_DATABASE = os.getenv('USE_DATABASE', 'True').lower() == 'true'  # Default to database
DB_TYPE = os.getenv('DB_TYPE', 'sqlite')  # 'sqlite' or 'postgresql'

# Database connection settings (for PostgreSQL)
DB_CONFIG = {
    'user': os.getenv('DB_USER', 'edfast_user'),
    'password': os.getenv('DB_PASSWORD', 'edfast_password'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'edfast_db')
}

# Migration settings
AUTO_MIGRATE = os.getenv('AUTO_MIGRATE', 'False').lower() == 'true'

# Feature flags
ENABLE_PEERHUB = True
ENABLE_TIMETABLE = True
ENABLE_RESUME_BUILDER = True
ENABLE_CHATBOT = True

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'edfast.log')

def get_storage_info():
    """Get current storage backend information."""
    if USE_DATABASE:
        return f"Database ({DB_TYPE})"
    else:
        return "JSON Files (Legacy)"

def print_config():
    """Print current configuration."""
    print("\n" + "=" * 60)
    print(" " * 20 + "EdFast Configuration")
    print("=" * 60)
    print(f"Storage Backend: {get_storage_info()}")
    print(f"PeerHub: {'Enabled' if ENABLE_PEERHUB else 'Disabled'}")
    print(f"Timetable: {'Enabled' if ENABLE_TIMETABLE else 'Disabled'}")
    print(f"Resume Builder: {'Enabled' if ENABLE_RESUME_BUILDER else 'Disabled'}")
    print(f"Chatbot: {'Enabled' if ENABLE_CHATBOT else 'Disabled'}")
    print("=" * 60 + "\n")


