from flask import jsonify
from marshmallow import ValidationError
from app.utils.helpers import error_response

def register_error_handlers(app):
    """Register error handlers for the Flask application"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return error_response(
            "BAD_REQUEST",
            "Bad request",
            status_code=400
        )
    
    @app.errorhandler(401)
    def unauthorized(error):
        return error_response(
            "UNAUTHORIZED",
            "Authentication required",
            status_code=401
        )
    
    @app.errorhandler(403)
    def forbidden(error):
        return error_response(
            "FORBIDDEN",
            "Access forbidden",
            status_code=403
        )
    
    @app.errorhandler(404)
    def not_found(error):
        return error_response(
            "NOT_FOUND",
            "Resource not found",
            status_code=404
        )
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return error_response(
            "METHOD_NOT_ALLOWED",
            "Method not allowed",
            status_code=405
        )
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        return error_response(
            "UNPROCESSABLE_ENTITY",
            "Request could not be processed",
            status_code=422
        )
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return error_response(
            "INTERNAL_SERVER_ERROR",
            "An internal server error occurred",
            status_code=500
        )
    
    @app.errorhandler(ValidationError)
    def validation_error(error):
        return error_response(
            "VALIDATION_ERROR",
            "Request validation failed",
            details=error.messages,
            status_code=400
        )
    
    @app.errorhandler(ValueError)
    def value_error(error):
        return error_response(
            "VALIDATION_ERROR",
            str(error),
            status_code=400
        )
    
    @app.errorhandler(Exception)
    def general_exception(error):
        app.logger.error(f"Unhandled exception: {str(error)}")
        return error_response(
            "INTERNAL_ERROR",
            "An unexpected error occurred",
            status_code=500
        )