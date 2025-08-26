from flask import Blueprint, request
from app.services.auth_service import AuthService
from app.utils.validators import UpdateProfileSchema, UpdatePhoneSchema
from app.utils.decorators import jwt_required_with_user, validate_json_schema, handle_exceptions
from app.utils.helpers import success_response, error_response

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
@jwt_required_with_user()
@handle_exceptions
def get_profile():
    """
    Get current user's profile
    
    GET /api/user/profile
    Headers: Authorization: Bearer <jwt_token>
    """
    user = request.current_user
    user_data = user.to_dict(include_active_package=True)
    
    return success_response(user_data, "Profile retrieved successfully")

@user_bp.route('/profile', methods=['PUT'])
@jwt_required_with_user()
@validate_json_schema(UpdateProfileSchema)
@handle_exceptions
def update_profile():
    """
    Update user's name and national ID
    
    PUT /api/user/profile
    Headers: Authorization: Bearer <jwt_token>
    {
        "name": "string (optional)",
        "national_id": "string (optional)"
    }
    """
    user = request.current_user
    data = request.validated_data
    
    # Update user profile
    name = data.get('name')
    national_id = data.get('national_id')
    
    user.update_profile(name=name, national_id=national_id)
    
    # Return updated user data
    updated_user_data = user.to_dict(include_active_package=True)
    
    return success_response(updated_user_data, "Profile updated successfully")

@user_bp.route('/phone', methods=['PUT'])
@jwt_required_with_user()
@validate_json_schema(UpdatePhoneSchema)
@handle_exceptions
def update_phone():
    """
    Change user's phone number with OTP verification
    
    PUT /api/user/phone
    Headers: Authorization: Bearer <jwt_token>
    {
        "new_phone_number": "+965XXXXXXXX",
        "otp_code": "12345"
    }
    """
    user = request.current_user
    data = request.validated_data
    
    new_phone_number = data['new_phone_number']
    otp_code = data['otp_code']
    
    auth_service = AuthService()
    
    # Verify OTP for phone change
    success, message = auth_service.verify_otp_for_phone_change(
        new_phone_number, 
        otp_code, 
        user.user_id
    )
    
    if not success:
        if "expired" in message.lower():
            error_code = "OTP_EXPIRED"
        elif "invalid" in message.lower():
            error_code = "INVALID_OTP"
        elif "used" in message.lower():
            error_code = "OTP_ALREADY_USED"
        elif "not found" in message.lower():
            error_code = "OTP_NOT_FOUND"
        else:
            error_code = "OTP_VERIFICATION_FAILED"
        
        return error_response(error_code, message, status_code=400)
    
    # Update user's phone number
    try:
        user.update_phone(new_phone_number)
        return success_response(
            {"phone_number": new_phone_number}, 
            "Phone number updated successfully"
        )
    except ValueError as e:
        return error_response("PHONE_EXISTS", str(e), status_code=400)

@user_bp.route('/send-phone-change-otp', methods=['POST'])
@jwt_required_with_user()
@handle_exceptions
def send_phone_change_otp():
    """
    Send OTP for phone number change
    
    POST /api/user/send-phone-change-otp
    Headers: Authorization: Bearer <jwt_token>
    {
        "new_phone_number": "+965XXXXXXXX"
    }
    """
    if not request.is_json:
        return error_response("INVALID_REQUEST", "Request must be JSON", status_code=400)
    
    data = request.get_json()
    if not data or 'new_phone_number' not in data:
        return error_response("INVALID_REQUEST", "new_phone_number is required", status_code=400)
    
    new_phone_number = data['new_phone_number']
    user = request.current_user
    
    # Validate phone number format
    from app.utils.validators import validate_kuwait_phone
    from marshmallow import ValidationError
    
    try:
        normalized_phone = validate_kuwait_phone(new_phone_number)
    except ValidationError as e:
        return error_response("INVALID_PHONE", str(e), status_code=400)
    
    # Check if phone number is already taken by another user
    from app.models.user import User
    existing_user = User.find_by_phone(normalized_phone)
    if existing_user and existing_user.user_id != user.user_id:
        return error_response("PHONE_EXISTS", "Phone number already exists", status_code=400)
    
    # Send OTP for phone change
    auth_service = AuthService()
    auth_service.set_user_context(user.user_id)
    
    success, message, response_data = auth_service.send_otp(normalized_phone, 'phone_change')
    
    if success:
        return success_response(response_data, message)
    else:
        return error_response("OTP_SEND_FAILED", message, status_code=400)