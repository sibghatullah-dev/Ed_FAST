"""
Database Configuration and Connection Management for EdFast.
Supports both PostgreSQL (production) and SQLite (development).
"""

import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import logging

from database.models import Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration and connection management."""
    
    def __init__(self, db_type='sqlite', db_url=None):
        """
        Initialize database configuration.
        
        Args:
            db_type: Database type ('sqlite' or 'postgresql')
            db_url: Optional custom database URL
        """
        self.db_type = db_type
        self.db_url = db_url or self._get_default_url()
        self.engine = None
        self.SessionLocal = None
        
    def _get_default_url(self):
        """Get default database URL based on type."""
        if self.db_type == 'sqlite':
            # SQLite database in the project root
            db_path = os.path.join(os.getcwd(), 'edfast.db')
            return f'sqlite:///{db_path}'
        elif self.db_type == 'postgresql':
            # PostgreSQL from environment variables or default
            user = os.getenv('DB_USER', 'edfast_user')
            password = os.getenv('DB_PASSWORD', 'edfast_password')
            host = os.getenv('DB_HOST', 'localhost')
            port = os.getenv('DB_PORT', '5432')
            database = os.getenv('DB_NAME', 'edfast_db')
            return f'postgresql://{user}:{password}@{host}:{port}/{database}'
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
    
    def init_engine(self):
        """Initialize database engine with appropriate settings."""
        if self.db_type == 'sqlite':
            # SQLite specific settings
            self.engine = create_engine(
                self.db_url,
                connect_args={'check_same_thread': False},
                poolclass=StaticPool,
                echo=False  # Set to True for SQL debugging
            )
            # Enable foreign key support for SQLite
            @event.listens_for(self.engine, "connect")
            def set_sqlite_pragma(dbapi_conn, connection_record):
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()
        else:
            # PostgreSQL settings
            self.engine = create_engine(
                self.db_url,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                echo=False  # Set to True for SQL debugging
            )
        
        # Create session factory
        self.SessionLocal = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        )
        
        logger.info(f"Database engine initialized: {self.db_type}")
        return self.engine
    
    def create_tables(self):
        """Create all database tables."""
        if not self.engine:
            self.init_engine()
        
        Base.metadata.create_all(bind=self.engine)
        logger.info("All database tables created successfully")
    
    def drop_tables(self):
        """Drop all database tables (use with caution!)."""
        if not self.engine:
            self.init_engine()
        
        Base.metadata.drop_all(bind=self.engine)
        logger.warning("All database tables dropped")
    
    @contextmanager
    def get_session(self):
        """
        Get database session with automatic cleanup.
        
        Usage:
            with db_config.get_session() as session:
                user = session.query(User).first()
        """
        if not self.SessionLocal:
            self.init_engine()
        
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            session.close()
    
    def get_db_session(self):
        """
        Get database session (for manual management).
        Remember to close the session after use.
        """
        if not self.SessionLocal:
            self.init_engine()
        return self.SessionLocal()
    
    def close_all_sessions(self):
        """Close all database sessions."""
        if self.SessionLocal:
            self.SessionLocal.remove()
    
    def test_connection(self):
        """Test database connection."""
        try:
            with self.get_session() as session:
                session.execute("SELECT 1")
            logger.info("Database connection successful")
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            return False


# Global database instance - default to SQLite for easier setup
db_config = DatabaseConfig(db_type='sqlite')


def init_database(db_type='sqlite', db_url=None, create_tables=True):
    """
    Initialize the database.
    
    Args:
        db_type: Database type ('sqlite' or 'postgresql')
        db_url: Optional custom database URL
        create_tables: Whether to create tables automatically
    
    Returns:
        DatabaseConfig instance
    """
    global db_config
    db_config = DatabaseConfig(db_type=db_type, db_url=db_url)
    db_config.init_engine()
    
    if create_tables:
        db_config.create_tables()
    
    return db_config


def get_db():
    """
    Dependency function to get database session.
    Used for dependency injection in services.
    """
    session = db_config.get_db_session()
    try:
        yield session
    finally:
        session.close()


def get_session():
    """Get a new database session."""
    return db_config.get_db_session()


