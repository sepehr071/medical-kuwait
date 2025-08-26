from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.auth_service import AuthService
from app.utils.helpers import error_response

def jwt_required_with_user():
    """
    Decorator that combines JWT requirement with user validation
    Sets current_user in the request context
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            try:
                # Get user ID from JWT token
                user_id = get_jwt_identity()
                if not user_id:
                    return error_response("INVALID_TOKEN", "Invalid or missing token", status_code=401)
                
                # Get user from database
                user = AuthService.get_user_from_token(user_id)
                if not user:
                    return error_response("USER_NOT_FOUND", "User not found or inactive", status_code=401)
                
                # Set user in request context for use in the endpoint
                request.current_user = user
                
                return f(*args, **kwargs)
            except Exception as e:
                return error_response("AUTH_ERROR", "Authentication failed", status_code=401)
        
        return decorated_function
    return decorator

def validate_json_schema(schema_class):
    """
    Decorator to validate request JSON against a marshmallow schema
    
    Args:
        schema_class: Marshmallow schema class to validate against
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from app.utils.helpers import validate_request_json
            
            # Check if request has JSON
            if not request.is_json:
                return error_response("INVALID_REQUEST", "Request must be JSON", status_code=400)
            
            json_data = request.get_json()
            if not json_data:
                return error_response("INVALID_REQUEST", "Request body is required", status_code=400)
            
            # Validate against schema
            schema = schema_class()
            validated_data, errors = validate_request_json(schema, json_data)
            
            if errors:
                return error_response(
                    "VALIDATION_ERROR", 
                    "Request validation failed", 
                    details=errors, 
                    status_code=400
                )
            
            # Set validated data in request context
            request.validated_data = validated_data
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def handle_exceptions(f):
    """
    Decorator to handle exceptions and return standardized error responses
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return error_response("VALIDATION_ERROR", str(e), status_code=400)
        except Exception as e:
            # Log the error for debugging
            from flask import current_app
            current_app.logger.error(f"Unhandled exception in {f.__name__}: {str(e)}")
            return error_response("INTERNAL_ERROR", "An internal error occurred", status_code=500)
    
    return decorated_function