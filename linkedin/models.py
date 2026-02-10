"""
LinkedIn Data Models for EdFast Platform
Database models for storing LinkedIn job and post data
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
import json

@dataclass
class LinkedInJob:
    """LinkedIn Job data model."""
    
    # Basic job information
    title: str
    company: str
    location: str
    description: str
    url: str
    
    # Job details
    posted_date: Optional[str] = None
    job_type: Optional[str] = None  # fulltime, parttime, internship, contract
    is_remote: bool = False
    
    # Salary information
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    currency: str = "USD"
    
    # Company information
    company_url: Optional[str] = None
    company_industry: Optional[str] = None
    company_num_employees: Optional[str] = None
    company_revenue: Optional[str] = None
    
    # Contact information
    emails: Optional[List[str]] = None
    
    # Metadata
    scraped_at: Optional[str] = None
    search_term: Optional[str] = None
    search_location: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LinkedInJob':
        """Create instance from dictionary."""
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'LinkedInJob':
        """Create instance from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

@dataclass
class LinkedInPost:
    """LinkedIn Post data model."""
    
    # Basic post information
    post_url: str
    content: str
    type: str  # Original, Shared
    
    # Engagement metrics
    like_count: str = "0"
    comment_count: str = "0"
    repost_count: str = "0"
    
    # Media information
    img_url: Optional[str] = None
    image_drive_link: Optional[str] = None
    
    # Post metadata
    post_date: Optional[str] = None
    profile_url: Optional[str] = None
    
    # Scraping metadata
    scraped_at: Optional[str] = None
    profile_name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LinkedInPost':
        """Create instance from dictionary."""
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'LinkedInPost':
        """Create instance from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

@dataclass
class LinkedInScrapingSession:
    """LinkedIn scraping session data model."""
    
    session_id: str
    session_type: str  # "job_scraping" or "post_scraping"
    search_params: Dict[str, Any]
    results_count: int
    started_at: str
    completed_at: Optional[str] = None
    status: str = "running"  # running, completed, failed
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LinkedInScrapingSession':
        """Create instance from dictionary."""
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'LinkedInScrapingSession':
        """Create instance from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

# Database table creation SQL (for SQLite)
LINKEDIN_JOBS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS linkedin_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT NOT NULL,
    description TEXT,
    url TEXT UNIQUE,
    posted_date TEXT,
    job_type TEXT,
    is_remote BOOLEAN DEFAULT 0,
    min_salary REAL,
    max_salary REAL,
    currency TEXT DEFAULT 'USD',
    company_url TEXT,
    company_industry TEXT,
    company_num_employees TEXT,
    company_revenue TEXT,
    emails TEXT,  -- JSON array
    scraped_at TEXT,
    search_term TEXT,
    search_location TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

LINKEDIN_POSTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS linkedin_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_url TEXT UNIQUE,
    content TEXT,
    type TEXT,
    like_count TEXT DEFAULT '0',
    comment_count TEXT DEFAULT '0',
    repost_count TEXT DEFAULT '0',
    img_url TEXT,
    image_drive_link TEXT,
    post_date TEXT,
    profile_url TEXT,
    scraped_at TEXT,
    profile_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

LINKEDIN_SESSIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS linkedin_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE,
    session_type TEXT,
    search_params TEXT,  -- JSON
    results_count INTEGER DEFAULT 0,
    started_at TEXT,
    completed_at TEXT,
    status TEXT DEFAULT 'running',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
