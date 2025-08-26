import uuid
import random
import string
from datetime import datetime, timedelta
from flask import jsonify
import bcrypt

def generate_uuid():
    """Generate a UUID string"""
    return str(uuid.uuid4())

def generate_otp():
    """Generate a 5-digit OTP code"""
    return ''.join(random.choices(string.digits, k=5))

def hash_otp(otp_code):
    """Hash OTP code using bcrypt"""
    return bcrypt.hashpw(otp_code.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_otp(plain_otp, hashed_otp):
    """Verify OTP code against hash"""
    return bcrypt.checkpw(plain_otp.encode('utf-8'), hashed_otp.encode('utf-8'))

def get_otp_expiry():
    """Get OTP expiry datetime (5 minutes from now)"""
    return datetime.utcnow() + timedelta(minutes=5)

def calculate_package_expiry(duration_days):
    """Calculate package expiry date"""
    return datetime.utcnow() + timedelta(days=duration_days)

def calculate_remaining_days(expires_at):
    """Calculate remaining days until expiry"""
    if not expires_at:
        return 0
    
    now = datetime.utcnow()
    if expires_at <= now:
        return 0
    
    delta = expires_at - now
    return delta.days

def success_response(data=None, message="Operation completed successfully"):
    """Create standardized success response"""
    response = {
        "success": True,
        "message": message
    }
    if data is not None:
        response["data"] = data
    return jsonify(response)

def error_response(code, message, details=None, status_code=400):
    """Create standardized error response"""
    response = {
        "success": False,
        "error": {
            "code": code,
            "message": message
        }
    }
    if details:
        response["error"]["details"] = details
    return jsonify(response), status_code

def validate_request_json(schema, json_data):
    """
    Validate request JSON against marshmallow schema
    
    Args:
        schema: Marshmallow schema instance
        json_data: JSON data to validate
        
    Returns:
        tuple: (validated_data, errors)
    """
    try:
        validated_data = schema.load(json_data)
        return validated_data, None
    except Exception as e:
        if hasattr(e, 'messages'):
            return None, e.messages
        return None, {"validation": [str(e)]}

def serialize_datetime(dt):
    """Serialize datetime to ISO format"""
    if dt:
        return dt.isoformat() + 'Z'
    return None

def parse_datetime(dt_string):
    """Parse ISO datetime string"""
    if dt_string:
        return datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
    return None