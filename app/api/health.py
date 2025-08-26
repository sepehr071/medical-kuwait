from flask import Blueprint, jsonify
from datetime import datetime
from app.config.database import get_db
from app.utils.helpers import success_response, error_response

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    System health check endpoint
    
    GET /api/health
    """
    try:
        # Test database connection
        db = get_db()
        db.command('ping')
        
        return success_response(
            {
                "status": "healthy",
                "services": {
                    "database": "connected",
                    "api": "running"
                },
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            },
            "System is healthy"
        )
    except Exception as e:
        return error_response(
            "HEALTH_CHECK_FAILED",
            f"System health check failed: {str(e)}",
            status_code=500
        )

@health_bp.route('/version', methods=['GET'])
def version_info():
    """
    API version information
    
    GET /api/version
    """
    return success_response(
        {
            "version": "1.0.0",
            "name": "Kuwait Medical Clinic API",
            "description": "Flask backend API for medical clinic system"
        },
        "Version information retrieved"
    )