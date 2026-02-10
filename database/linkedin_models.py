"""
LinkedIn Database Models for EdFast Platform
SQLAlchemy models for storing LinkedIn job and post data
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import json

Base = declarative_base()

class LinkedInJob(Base):
    """LinkedIn Job database model."""
    
    __tablename__ = 'linkedin_jobs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Basic job information
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    description = Column(Text)
    url = Column(String(500), unique=True, nullable=False)
    
    # Job details
    posted_date = Column(String(100))
    job_type = Column(String(50))  # fulltime, parttime, internship, contract
    is_remote = Column(Boolean, default=False)
    
    # Salary information
    min_salary = Column(Float)
    max_salary = Column(Float)
    currency = Column(String(10), default='USD')
    
    # Company information
    company_url = Column(String(500))
    company_industry = Column(String(255))
    company_num_employees = Column(String(100))
    company_revenue = Column(String(100))
    
    # Contact information (stored as JSON)
    emails = Column(JSON)
    
    # Search metadata
    search_term = Column(String(255))
    search_location = Column(String(255))
    
    # Timestamps
    scraped_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'description': self.description,
            'url': self.url,
            'posted_date': self.posted_date,
            'job_type': self.job_type,
            'is_remote': self.is_remote,
            'min_salary': self.min_salary,
            'max_salary': self.max_salary,
            'currency': self.currency,
            'company_url': self.company_url,
            'company_industry': self.company_industry,
            'company_num_employees': self.company_num_employees,
            'company_revenue': self.company_revenue,
            'emails': self.emails,
            'search_term': self.search_term,
            'search_location': self.search_location,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create instance from dictionary."""
        # Handle emails conversion
        if isinstance(data.get('emails'), str):
            try:
                data['emails'] = json.loads(data['emails'])
            except:
                data['emails'] = []
        
        # Remove id if present (will be auto-generated)
        data.pop('id', None)
        data.pop('created_at', None)
        data.pop('updated_at', None)
        
        return cls(**data)

class LinkedInPost(Base):
    """LinkedIn Post database model."""
    
    __tablename__ = 'linkedin_posts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Basic post information
    post_url = Column(String(500), unique=True, nullable=False)
    content = Column(Text)
    type = Column(String(50))  # Original, Shared
    
    # Engagement metrics
    like_count = Column(String(20), default='0')
    comment_count = Column(String(20), default='0')
    repost_count = Column(String(20), default='0')
    
    # Media information
    img_url = Column(String(500))
    image_drive_link = Column(String(500))
    
    # Post metadata
    post_date = Column(String(100))
    profile_url = Column(String(500))
    profile_name = Column(String(255))
    
    # Timestamps
    scraped_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'post_url': self.post_url,
            'content': self.content,
            'type': self.type,
            'like_count': self.like_count,
            'comment_count': self.comment_count,
            'repost_count': self.repost_count,
            'img_url': self.img_url,
            'image_drive_link': self.image_drive_link,
            'post_date': self.post_date,
            'profile_url': self.profile_url,
            'profile_name': self.profile_name,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create instance from dictionary."""
        # Remove id if present (will be auto-generated)
        data.pop('id', None)
        data.pop('created_at', None)
        data.pop('updated_at', None)
        
        return cls(**data)

class LinkedInScrapingSession(Base):
    """LinkedIn scraping session database model."""
    
    __tablename__ = 'linkedin_sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), unique=True, nullable=False)
    session_type = Column(String(50), nullable=False)  # job_scraping, post_scraping
    search_params = Column(JSON)  # Store search parameters as JSON
    results_count = Column(Integer, default=0)
    status = Column(String(50), default='running')  # running, completed, failed
    error_message = Column(Text)
    
    # Timestamps
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'session_type': self.session_type,
            'search_params': self.search_params,
            'results_count': self.results_count,
            'status': self.status,
            'error_message': self.error_message,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create instance from dictionary."""
        # Remove id if present (will be auto-generated)
        data.pop('id', None)
        data.pop('created_at', None)
        data.pop('updated_at', None)
        
        return cls(**data)

# Database service functions
class LinkedInDatabaseService:
    """Service class for LinkedIn database operations."""
    
    def __init__(self, db_session):
        self.db = db_session
    
    def save_job(self, job_data):
        """Save a LinkedIn job to the database."""
        try:
            # Check if job already exists
            existing_job = self.db.query(LinkedInJob).filter_by(url=job_data['url']).first()
            if existing_job:
                return existing_job
            
            # Create new job
            job = LinkedInJob.from_dict(job_data)
            self.db.add(job)
            self.db.commit()
            return job
        except Exception as e:
            self.db.rollback()
            raise e
    
    def save_post(self, post_data):
        """Save a LinkedIn post to the database."""
        try:
            # Check if post already exists
            existing_post = self.db.query(LinkedInPost).filter_by(post_url=post_data['post_url']).first()
            if existing_post:
                return existing_post
            
            # Create new post
            post = LinkedInPost.from_dict(post_data)
            self.db.add(post)
            self.db.commit()
            return post
        except Exception as e:
            self.db.rollback()
            raise e
    
    def save_session(self, session_data):
        """Save a LinkedIn scraping session to the database."""
        try:
            session = LinkedInScrapingSession.from_dict(session_data)
            self.db.add(session)
            self.db.commit()
            return session
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_jobs_by_search(self, search_term=None, location=None, limit=50):
        """Get jobs by search criteria."""
        query = self.db.query(LinkedInJob)
        
        if search_term:
            query = query.filter(LinkedInJob.search_term.ilike(f'%{search_term}%'))
        if location:
            query = query.filter(LinkedInJob.search_location.ilike(f'%{location}%'))
        
        return query.order_by(LinkedInJob.created_at.desc()).limit(limit).all()
    
    def get_posts_by_profile(self, profile_url=None, limit=50):
        """Get posts by profile URL."""
        query = self.db.query(LinkedInPost)
        
        if profile_url:
            query = query.filter(LinkedInPost.profile_url.ilike(f'%{profile_url}%'))
        
        return query.order_by(LinkedInPost.created_at.desc()).limit(limit).all()
    
    def get_recent_sessions(self, limit=20):
        """Get recent scraping sessions."""
        return self.db.query(LinkedInScrapingSession).order_by(
            LinkedInScrapingSession.created_at.desc()
        ).limit(limit).all()
