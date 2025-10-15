"""
Configuration settings for the Meeting Notes App.
Supports different environments (development, production).
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    """Base configuration class with default settings."""
    
    # Flask settings
    SECRET_KEY = (
        os.environ.get('SECRET_KEY') or
        'dev-secret-key-change-in-production'
    )
    
    # Database settings
    # Use PostgreSQL in production (Heroku), SQLite for local development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'dev.db')
    
    # Fix for Heroku postgres:// -> postgresql://
    if (SQLALCHEMY_DATABASE_URI and
            SQLALCHEMY_DATABASE_URI.startswith('postgres://')):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
            'postgres://', 'postgresql://', 1
        )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Login settings
    REMEMBER_COOKIE_DURATION = 3600  # 1 hour
    
    # Pagination
    ITEMS_PER_PAGE = 10


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    FLASK_ENV = 'development'


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    FLASK_ENV = 'production'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
