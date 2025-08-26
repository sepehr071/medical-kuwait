from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.config.database import init_db
from app.config.settings import config
import os

def create_app(config_name='development'):
    """Flask application factory"""
    app = Flask(__name__)
    
    # Load configuration
    config_class = config.get(config_name, config['default'])
    app.config.from_object(config_class)
    
    # Initialize extensions
    jwt = JWTManager(app)
    CORS(app, origins=[app.config.get('FRONTEND_URL', 'http://localhost:3000')])
    
    # Initialize database
    init_db(app)
    
    # Register blueprints
    from app.api.auth import auth_bp
    from app.api.user import user_bp
    from app.api.packages import packages_bp
    from app.api.health import health_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(packages_bp, url_prefix='/api/packages')
    app.register_blueprint(health_bp, url_prefix='/api')
    
    # Error handlers
    from app.api.errors import register_error_handlers
    register_error_handlers(app)
    
    return app