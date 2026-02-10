"""
Database-backed user management service for EdFast application.
Replaces JSON-based user_management.py with SQLAlchemy database operations.
"""

import hashlib
import json
from datetime import datetime
from typing import Optional, Dict, List
from sqlalchemy.exc import IntegrityError

from database.models import User
from database.db_config import get_session


def hash_password(password: str) -> str:
    """Hash password using SHA-256 (upgrade to bcrypt in production)."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    return hash_password(password) == hashed


class UserService:
    """Service class for user management operations."""
    
    @staticmethod
    def user_exists(username: str) -> bool:
        """Check if a username already exists."""
        session = get_session()
        try:
            user = session.query(User).filter(User.username == username).first()
            return user is not None
        finally:
            session.close()
    
    @staticmethod
    def validate_login(username: str, password: str) -> bool:
        """Validate login credentials."""
        session = get_session()
        try:
            user = session.query(User).filter(User.username == username).first()
            if user and verify_password(password, user.password):
                # Update last login
                user.last_login = datetime.utcnow()
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    @staticmethod
    def add_user(name: str, username: str, password: str, email: str = "") -> bool:
        """Add a new user."""
        session = get_session()
        try:
            # Check if user already exists
            if UserService.user_exists(username):
                return False
            
            # Create new user
            user = User(
                username=username,
                password=hash_password(password),
                name=name,
                email=email,
                transcript_file='',
                transcript_data={},
                description='',
                resume_data={}
            )
            
            session.add(user)
            session.commit()
            return True
        except IntegrityError:
            session.rollback()
            return False
        finally:
            session.close()
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """Get user object by username."""
        session = get_session()
        try:
            return session.query(User).filter(User.username == username).first()
        finally:
            session.close()
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[User]:
        """Get user object by ID."""
        session = get_session()
        try:
            return session.query(User).filter(User.id == user_id).first()
        finally:
            session.close()
    
    @staticmethod
    def get_user_transcript(username: str) -> str:
        """Get a user's transcript file path."""
        session = get_session()
        try:
            user = session.query(User).filter(User.username == username).first()
            return user.transcript_file if user else ''
        finally:
            session.close()
    
    @staticmethod
    def get_user_transcript_data(username: str) -> Dict:
        """Get a user's parsed transcript data."""
        session = get_session()
        try:
            user = session.query(User).filter(User.username == username).first()
            return user.transcript_data if user else {}
        finally:
            session.close()
    
    @staticmethod
    def update_user_transcript(username: str, transcript_file: str, transcript_data: Dict = None):
        """Update user's transcript file and data."""
        session = get_session()
        try:
            user = session.query(User).filter(User.username == username).first()
            if user:
                user.transcript_file = transcript_file
                if transcript_data is not None:
                    user.transcript_data = transcript_data
                user.updated_at = datetime.utcnow()
                session.commit()
        finally:
            session.close()
    
    @staticmethod
    def update_user_description(username: str, description: str):
        """Update user's description."""
        session = get_session()
        try:
            user = session.query(User).filter(User.username == username).first()
            if user:
                user.description = description
                user.updated_at = datetime.utcnow()
                session.commit()
        finally:
            session.close()
    
    @staticmethod
    def get_user_description(username: str) -> str:
        """Get user's description."""
        session = get_session()
        try:
            user = session.query(User).filter(User.username == username).first()
            return user.description if user else ''
        finally:
            session.close()
    
    @staticmethod
    def get_user_resume_data(username: str) -> Dict:
        """Get user's resume data."""
        session = get_session()
        try:
            user = session.query(User).filter(User.username == username).first()
            return user.resume_data if user else {}
        finally:
            session.close()
    
    @staticmethod
    def update_user_resume_data(username: str, resume_data: Dict):
        """Update user's resume data."""
        session = get_session()
        try:
            user = session.query(User).filter(User.username == username).first()
            if user:
                user.resume_data = resume_data
                user.updated_at = datetime.utcnow()
                session.commit()
        finally:
            session.close()
    
    @staticmethod
    def get_user_name(username: str) -> str:
        """Get user's full name."""
        session = get_session()
        try:
            user = session.query(User).filter(User.username == username).first()
            return user.name if user else 'Full Name'
        finally:
            session.close()
    
    @staticmethod
    def get_all_users() -> List[User]:
        """Get all users."""
        session = get_session()
        try:
            return session.query(User).all()
        finally:
            session.close()
    
    @staticmethod
    def update_user_profile(username: str, **kwargs):
        """Update user profile with arbitrary fields."""
        session = get_session()
        try:
            user = session.query(User).filter(User.username == username).first()
            if user:
                for key, value in kwargs.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                user.updated_at = datetime.utcnow()
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    @staticmethod
    def delete_user(username: str) -> bool:
        """Delete a user (soft delete by setting is_deleted flag or hard delete)."""
        session = get_session()
        try:
            user = session.query(User).filter(User.username == username).first()
            if user:
                session.delete(user)
                session.commit()
                return True
            return False
        finally:
            session.close()


# Backward compatibility functions (same interface as old user_management.py)
def create_user_storage_if_not_exists():
    """No-op for database - tables are created automatically."""
    pass


def user_exists(username: str) -> bool:
    """Check if a username already exists."""
    return UserService.user_exists(username)


def validate_login(username: str, password: str) -> bool:
    """Validate login credentials."""
    return UserService.validate_login(username, password)


def get_user_transcript(username: str) -> str:
    """Get a user's transcript file."""
    return UserService.get_user_transcript(username)


def add_user(name: str, username: str, password: str) -> bool:
    """Add a new user."""
    return UserService.add_user(name, username, password)


def update_user_transcript(username: str, transcript_file: str):
    """Update user's transcript file."""
    UserService.update_user_transcript(username, transcript_file)


def update_user_description(username: str, description: str):
    """Update user's description."""
    UserService.update_user_description(username, description)


def get_user_resume_data(username: str) -> Dict:
    """Get user's resume data."""
    return UserService.get_user_resume_data(username)


def update_user_resume_data(username: str, resume_data: Dict):
    """Update user's resume data."""
    UserService.update_user_resume_data(username, resume_data)


def get_user_description(username: str) -> str:
    """Get user's description."""
    return UserService.get_user_description(username)


def get_user_name(username: str) -> str:
    """Get user's full name."""
    return UserService.get_user_name(username)


