"""
Flask application factory and initialization.
Creates and configures the Flask app with all extensions.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app(config_name='default'):
    """
    Application factory pattern.
    Creates and configures a Flask application instance.
    
    Args:
        config_name: Configuration environment
            ('development', 'production', 'default')
    
    Returns:
        Configured Flask app instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Configure Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.meetings import meetings_bp
    from app.routes.notes import notes_bp
    from app.routes.attendees import attendees_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(meetings_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(attendees_bp)
    
    # Register main routes
    from app.routes import main
    app.register_blueprint(main.main_bp)
    
    return app
