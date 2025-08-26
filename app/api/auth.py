from flask import Blueprint, request
from app.services.auth_service import AuthService
from app.utils.validators import SendOTPSchema, VerifyOTPSchema
from app.utils.decorators import validate_json_schema, handle_exceptions
from app.utils.helpers import success_response, error_response

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/send-otp', methods=['POST'])
@validate_json_schema(SendOTPSchema)
@handle_exceptions
def send_otp():
    """
    Send OTP code to phone number for login or phone change
    
    POST /api/auth/send-otp
    {
        "phone_number": "+965XXXXXXXX",
        "purpose": "login|phone_change"
    }
    """
    data = request.validated_data
    phone_number = data['phone_number']
    purpose = data['purpose']
    
    auth_service = AuthService()
    
    # For phone_change purpose, we need user context (this would be set by the calling endpoint)
    if purpose == 'phone_change':
        # This endpoint should only be called for login purpose
        # Phone change OTP should be handled by the user profile update endpoint
        return error_response(
            "INVALID_PURPOSE", 
            "Use /api/user/phone endpoint for phone change OTP",
            status_code=400
        )
    
    success, message, data = auth_service.send_otp(phone_number, purpose)
    
    if success:
        return success_response(data, message)
    else:
        return error_response("OTP_SEND_FAILED", message, status_code=400)

@auth_bp.route('/verify-otp', methods=['POST'])
@validate_json_schema(VerifyOTPSchema)
@handle_exceptions
def verify_otp():
    """
    Verify OTP and authenticate user
    
    POST /api/auth/verify-otp
    {
        "phone_number": "+965XXXXXXXX",
        "code": "12345"
    }
    """
    data = request.validated_data
    phone_number = data['phone_number']
    code = data['code']
    
    auth_service = AuthService()
    success, message, response_data = auth_service.verify_otp_and_login(phone_number, code)
    
    if success:
        return success_response(response_data, message)
    else:
        if "expired" in message.lower():
            error_code = "OTP_EXPIRED"
        elif "invalid" in message.lower():
            error_code = "INVALID_OTP"
        elif "used" in message.lower():
            error_code = "OTP_ALREADY_USED"
        else:
            error_code = "OTP_VERIFICATION_FAILED"
        
        return error_response(error_code, message, status_code=400)