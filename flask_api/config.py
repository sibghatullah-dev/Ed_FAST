"""
Flask API Configuration
"""

import os
from datetime import timedelta


class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'edfast-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # File upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'xlsx', 'xls', 'csv'}
    
    # CORS - Allow localhost (development) and dev tunnel domains
    CORS_ORIGINS = [
        'http://localhost:3000', 
        'http://localhost:3001',
        'https://x7mq0j1w-3000.asse.devtunnels.ms',
        'http://x7mq0j1w-3000.asse.devtunnels.ms'
    ]
    
    # Database
    USE_DATABASE = os.getenv('USE_DATABASE', 'True').lower() == 'true'
    DB_TYPE = os.getenv('DB_TYPE', 'sqlite')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}




