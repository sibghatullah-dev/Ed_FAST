"""
User management module for EdFast application.
Handles user authentication, registration, and user data management.
"""

import json
import os
from config.constants import USERS_FILE


def create_user_storage_if_not_exists():
    """Create the user storage JSON file if it doesn't exist."""
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump([], f)


def user_exists(username):
    """Check if a username already exists."""
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
        return any(user['username'] == username for user in users)


def validate_login(username, password):
    """Validate login credentials."""
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
        for user in users:
            if user['username'] == username and user['password'] == password:
                return True
    return False


def get_user_transcript(username):
    """Get a user's transcript file."""
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
        for user in users:
            if user['username'] == username:
                return user.get('transcript_file', '')
    return None


def add_user(name, username, password):
    """Add a new user."""
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    
    users.append({
        'name': name,
        'username': username,
        'password': password,
        'transcript_file': ''  # Empty initially, will be updated after upload
    })
    
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)


def update_user_transcript(username, transcript_file):
    """Update user's transcript file."""
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    
    for user in users:
        if user['username'] == username:
            user['transcript_file'] = transcript_file
            break
    
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)


def update_user_description(username, description):
    """Update user's description."""
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    
    for user in users:
        if user['username'] == username:
            user['description'] = description
            break
    
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)


def get_user_resume_data(username):
    """Get user's resume data."""
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
        for user in users:
            if user['username'] == username:
                return user.get('resume_data', {})
    return {}


def update_user_resume_data(username, resume_data):
    """Update user's resume data."""
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    
    for user in users:
        if user['username'] == username:
            user['resume_data'] = resume_data
            break
    
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)


def get_user_description(username):
    """Get user's description."""
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
        for user in users:
            if user['username'] == username:
                return user.get('description', '')
    return ''


def get_user_name(username):
    """Get user's full name."""
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
        for user in users:
            if user['username'] == username:
                return user.get('name', 'Full Name')
    return 'Full Name' 