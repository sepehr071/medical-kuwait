from flask import current_app
from flask_jwt_extended import create_access_token
from app.models.user import User
from app.models.otp import OTPCode
from app.services.sms_service import SMSService
from app.utils.helpers import generate_otp
from app.utils.validators import validate_kuwait_phone

class AuthService:
    """Authentication service for OTP and JWT management"""
    
    def __init__(self):
        try:
            self.sms_service = SMSService()
        except Exception as e:
            current_app.logger.error(f"Failed to initialize SMS service: {str(e)}")
            self.sms_service = None
    
    def send_otp(self, phone_number, purpose='login'):
        """
        Send OTP to phone number
        
        Args:
            phone_number (str): Phone number to send OTP to
            purpose (str): Purpose of OTP ('login' or 'phone_change')
            
        Returns:
            tuple: (success, message, data)
        """
        try:
            # Validate and normalize phone number
            normalized_phone = validate_kuwait_phone(phone_number)
            
            # Invalidate any previous OTPs for this phone and purpose
            OTPCode.invalidate_previous_otps(normalized_phone, purpose)
            
            # Generate new OTP
            otp_code = generate_otp()
            
            # For phone_change, we need to get user_id from context
            user_id = None
            if purpose == 'phone_change':
                # This would be set by the calling endpoint
                user_id = getattr(self, '_current_user_id', None)
            
            # Create OTP record
            otp = OTPCode(
                phone_number=normalized_phone,
                code=otp_code,
                purpose=purpose,
                user_id=user_id
            )
            otp.save()
            
            # Send SMS
            if self.sms_service is None:
                current_app.logger.error("SMS service not available")
                return False, "SMS service is not configured properly. Please contact support.", None
            
            sms_sent = self.sms_service.send_otp(normalized_phone, otp_code, purpose)
            
            if sms_sent:
                return True, "OTP sent successfully", {
                    "message": "OTP sent successfully",
                    "expires_in": 300  # 5 minutes
                }
            else:
                return False, "Failed to send OTP. Please try again or contact support.", None
                
        except Exception as e:
            current_app.logger.error(f"Error sending OTP: {str(e)}")
            return False, str(e), None
    
    def verify_otp_and_login(self, phone_number, code):
        """
        Verify OTP and login user
        
        Args:
            phone_number (str): Phone number
            code (str): OTP code
            
        Returns:
            tuple: (success, message, user_data_with_token)
        """
        try:
            # Validate and normalize phone number
            normalized_phone = validate_kuwait_phone(phone_number)
            
            # Find OTP
            otp = OTPCode.find_by_phone_and_purpose(normalized_phone, 'login')
            if not otp:
                return False, "No valid OTP found", None
            
            # Verify OTP
            is_valid, message = otp.verify(code)
            if not is_valid:
                return False, message, None
            
            # Mark OTP as used
            otp.mark_as_used()
            
            # Get or create user
            user = User.find_by_phone(normalized_phone)
            if not user:
                # Create new user
                user = User(phone_number=normalized_phone)
                user.save()
            
            # Check if user is active
            if not user.is_active:
                return False, "User account is inactive", None
            
            # Generate JWT token
            token = create_access_token(
                identity=user.user_id,
                additional_claims={
                    'phone_number': user.phone_number
                }
            )
            
            # Prepare user data
            user_data = user.to_dict(include_active_package=True)
            
            return True, "Login successful", {
                "user": user_data,
                "token": token
            }
            
        except Exception as e:
            current_app.logger.error(f"Error verifying OTP: {str(e)}")
            return False, str(e), None
    
    def verify_otp_for_phone_change(self, phone_number, code, user_id):
        """
        Verify OTP for phone change
        
        Args:
            phone_number (str): New phone number
            code (str): OTP code
            user_id (str): Current user ID
            
        Returns:
            tuple: (success, message)
        """
        try:
            # Validate and normalize phone number
            normalized_phone = validate_kuwait_phone(phone_number)
            
            # Find OTP
            otp = OTPCode.find_by_phone_and_purpose(normalized_phone, 'phone_change')
            if not otp:
                return False, "No valid OTP found"
            
            # Verify OTP belongs to the current user
            if otp.user_id != user_id:
                return False, "OTP not associated with current user"
            
            # Verify OTP
            is_valid, message = otp.verify(code)
            if not is_valid:
                return False, message
            
            # Mark OTP as used
            otp.mark_as_used()
            
            return True, "OTP verified successfully"
            
        except Exception as e:
            current_app.logger.error(f"Error verifying phone change OTP: {str(e)}")
            return False, str(e)
    
    def set_user_context(self, user_id):
        """Set current user context for phone change OTP"""
        self._current_user_id = user_id
    
    @staticmethod
    def get_user_from_token(user_id):
        """Get user data from JWT token user_id"""
        try:
            user = User.find_by_id(user_id)
            if user and user.is_active:
                return user
            return None
        except Exception as e:
            current_app.logger.error(f"Error getting user from token: {str(e)}")
            return None