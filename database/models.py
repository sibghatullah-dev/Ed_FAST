"""
SQLAlchemy Database Models for EdFast Application.
Defines all database tables and relationships.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


def generate_uuid():
    """Generate a unique UUID string."""
    return str(uuid.uuid4())


class User(Base):
    """User model for authentication and profile management."""
    
    __tablename__ = 'users'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)  # Will store hashed passwords
    name = Column(String(200), nullable=False)
    email = Column(String(200))
    
    # Profile data
    transcript_file = Column(String(500))
    transcript_data = Column(JSON)  # Stores parsed transcript JSON
    description = Column(Text)
    resume_data = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime)
    
    # Relationships
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="user", cascade="all, delete-orphan")
    timetables = relationship("Timetable", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(username='{self.username}', name='{self.name}')>"


class Post(Base):
    """Post model for PeerHub discussions."""
    
    __tablename__ = 'posts'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    
    # Post metadata
    tags = Column(JSON)  # List of tags
    file_link = Column(String(500))
    course_code = Column(String(50))
    course_name = Column(String(200))
    semester = Column(Integer)
    
    # Engagement metrics
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    
    # Flags
    is_pinned = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="post", cascade="all, delete-orphan")
    
    @property
    def score(self):
        return self.upvotes - self.downvotes
    
    def __repr__(self):
        return f"<Post(id='{self.id}', title='{self.title[:30]}...')>"


class Comment(Base):
    """Comment model for post discussions."""
    
    __tablename__ = 'comments'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    post_id = Column(String(36), ForeignKey('posts.id'), nullable=False)
    author_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    
    # Nested comments support
    parent_id = Column(String(36), ForeignKey('comments.id'))
    
    # Engagement metrics
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    
    # Flags
    is_deleted = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")
    votes = relationship("Vote", back_populates="comment", cascade="all, delete-orphan")
    
    @property
    def score(self):
        return self.upvotes - self.downvotes
    
    def __repr__(self):
        return f"<Comment(id='{self.id}', post_id='{self.post_id}')>"


class Vote(Base):
    """Vote model for posts and comments."""
    
    __tablename__ = 'votes'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    
    # Polymorphic voting - can vote on posts or comments
    post_id = Column(String(36), ForeignKey('posts.id'))
    comment_id = Column(String(36), ForeignKey('comments.id'))
    
    vote_type = Column(String(10), nullable=False)  # 'upvote' or 'downvote'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="votes")
    post = relationship("Post", back_populates="votes")
    comment = relationship("Comment", back_populates="votes")
    
    def __repr__(self):
        target = f"post:{self.post_id}" if self.post_id else f"comment:{self.comment_id}"
        return f"<Vote(user_id='{self.user_id}', {target}, type='{self.vote_type}')>"


class Timetable(Base):
    """Timetable model for storing user timetable data."""
    
    __tablename__ = 'timetables'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    
    # Timetable metadata
    name = Column(String(200))
    semester = Column(String(50))
    academic_year = Column(String(20))
    
    # Timetable entries (stored as JSON array)
    entries = Column(JSON, nullable=False)  # List of timetable entries
    
    # File information
    original_filename = Column(String(500))
    
    # Settings
    selected_courses = Column(JSON)  # List of selected course codes
    selected_departments = Column(JSON)  # List of selected departments
    
    # Flags
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="timetables")
    
    def __repr__(self):
        return f"<Timetable(id='{self.id}', user_id='{self.user_id}', name='{self.name}')>"


class Course(Base):
    """Course model for storing course information."""
    
    __tablename__ = 'courses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_code = Column(String(50), unique=True, nullable=False, index=True)
    course_name = Column(String(200), nullable=False)
    semester = Column(Integer)
    credit_hours = Column(Integer)
    
    # Course details
    description = Column(Text)
    prerequisites = Column(JSON)  # List of prerequisite course codes
    is_elective = Column(Boolean, default=False)
    department = Column(String(100))
    
    # Additional metadata stored as JSON
    course_metadata = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Course(code='{self.course_code}', name='{self.course_name}')>"


class Transcript(Base):
    """Transcript model for storing processed transcript data."""
    
    __tablename__ = 'transcripts'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, unique=True)
    
    # Academic information
    student_id = Column(String(50))
    program = Column(String(200))
    department = Column(String(200))
    
    # Academic metrics
    cgpa = Column(Float)
    total_credits = Column(Integer)
    
    # Semesters data (stored as JSON)
    semesters = Column(JSON)  # List of semester objects with courses
    
    # Achievements and activities
    achievements = Column(JSON)
    extracurricular = Column(JSON)
    
    # Processing metadata
    image_path = Column(String(500))
    processing_status = Column(String(50), default='pending')  # pending, processing, completed, failed
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Transcript(user_id='{self.user_id}', cgpa={self.cgpa})>"


class SearchHistory(Base):
    """Search history for PeerHub analytics."""
    
    __tablename__ = 'search_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey('users.id'))
    
    query = Column(String(500), nullable=False)
    filters = Column(JSON)  # Stores applied filters
    results_count = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<SearchHistory(query='{self.query}', results={self.results_count})>"


class ActivityLog(Base):
    """Activity log for tracking user actions."""
    
    __tablename__ = 'activity_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey('users.id'))
    
    action_type = Column(String(50), nullable=False)  # login, post_create, comment_create, etc.
    action_data = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<ActivityLog(user_id='{self.user_id}', action='{self.action_type}')>"

