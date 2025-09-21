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
    try:
        data = request.validated_data
        phone_number = data['phone_number']
        purpose = data['purpose']
        
        # Log the request for debugging
        from flask import current_app
        current_app.logger.info(f"Send OTP request - Phone: {phone_number}, Purpose: {purpose}")
        
        # For phone_change purpose, we need user context (this would be set by the calling endpoint)
        if purpose == 'phone_change':
            # This endpoint should only be called for login purpose
            # Phone change OTP should be handled by the user profile update endpoint
            return error_response(
                "INVALID_PURPOSE",
                "Use /api/user/phone endpoint for phone change OTP",
                status_code=400
            )
        
        auth_service = AuthService()
        success, message, response_data = auth_service.send_otp(phone_number, purpose)
        
        current_app.logger.info(f"Send OTP result - Success: {success}, Message: {message}")
        
        if success:
            return success_response(response_data, message)
        else:
            return error_response("OTP_SEND_FAILED", message, status_code=400)
            
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Send OTP endpoint error: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return error_response("INTERNAL_ERROR", "An error occurred while processing your request", status_code=500)

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
        

@auth_bp.route('/debug', methods=['GET'])
def debug_info():
    """
    Debug endpoint to check SMS service configuration
    
    GET /api/auth/debug
    """
    try:
        from flask import current_app
        import os
        
        debug_info = {
            "twilio_config": {
                "account_sid": "Present" if os.getenv('TWILIO_ACCOUNT_SID') else "Missing",
                "auth_token": "Present" if os.getenv('TWILIO_AUTH_TOKEN') else "Missing", 
                "sms_from": os.getenv('TWILIO_SMS_FROM', 'Missing')
            },
            "flask_config": {
                "flask_env": os.getenv('FLASK_ENV', 'development'),
                "flask_debug": os.getenv('FLASK_DEBUG', 'False'),
                "flask_port": os.getenv('FLASK_PORT', '5000')
            }
        }
        
        # Test SMS service initialization
        try:
            from app.services.sms_service import SMSService
            sms_service = SMSService()
            debug_info["sms_service"] = "Initialized successfully"
        except Exception as e:
            debug_info["sms_service"] = f"Failed: {str(e)}"
        
        return success_response(debug_info, "Debug information")
        
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Debug endpoint error: {str(e)}")
        return error_response("DEBUG_ERROR", f"Debug failed: {str(e)}", status_code=500)
        return error_response(error_code, message, status_code=400)