import re
from marshmallow import Schema, fields, validate, ValidationError

# Kuwait phone number patterns
KUWAIT_PHONE_PATTERNS = [
    r'^\+965[56789]\d{7}$',      # +965XXXXXXXX
    r'^965[56789]\d{7}$',        # 965XXXXXXXX  
    r'^[56789]\d{7}$'            # 8-digit local
]

def validate_kuwait_phone(phone: str) -> str:
    """
    Validate and normalize Kuwait phone number
    
    Args:
        phone (str): Phone number to validate
        
    Returns:
        str: Normalized phone number in +965XXXXXXXX format
        
    Raises:
        ValidationError: If phone number is invalid
    """
    if not phone:
        raise ValidationError("Phone number is required")
    
    # Remove spaces and special chars except +
    cleaned = re.sub(r'[^\d+]', '', str(phone))
    
    # Normalize to +965XXXXXXXX format
    for pattern in KUWAIT_PHONE_PATTERNS:
        if re.match(pattern, cleaned):
            if cleaned.startswith('+965'):
                return cleaned
            elif cleaned.startswith('965'):
                return '+' + cleaned
            else:  # 8-digit local
                return '+965' + cleaned
    
    raise ValidationError("Invalid Kuwait phone number format. Must be Kuwait number starting with 5, 6, or 9")

# Custom field for Kuwait phone validation
class KuwaitPhoneField(fields.String):
    """Custom marshmallow field for Kuwait phone validation"""
    
    def _deserialize(self, value, attr, data, **kwargs):
        value = super()._deserialize(value, attr, data, **kwargs)
        if value:
            return validate_kuwait_phone(value)
        return value

# Validation schemas
class SendOTPSchema(Schema):
    phone_number = KuwaitPhoneField(required=True)
    purpose = fields.Str(
        required=True, 
        validate=validate.OneOf(['login', 'phone_change'])
    )

class VerifyOTPSchema(Schema):
    phone_number = KuwaitPhoneField(required=True)
    code = fields.Str(
        required=True, 
        validate=[
            validate.Length(equal=5),
            validate.Regexp(r'^\d{5}$', error="OTP must be 5 digits")
        ]
    )

class UpdateProfileSchema(Schema):
    name = fields.Str(
        validate=validate.Length(max=100),
        allow_none=True,
        required=False
    )
    national_id = fields.Str(
        validate=validate.Length(max=50),
        allow_none=True,
        required=False
    )

class UpdatePhoneSchema(Schema):
    new_phone_number = KuwaitPhoneField(required=True)
    otp_code = fields.Str(
        required=True,
        validate=[
            validate.Length(equal=5),
            validate.Regexp(r'^\d{5}$', error="OTP must be 5 digits")
        ]
    )

class PurchasePackageSchema(Schema):
    package_id = fields.Str(required=True)
    user_info = fields.Nested({
        'name': fields.Str(required=True, validate=validate.Length(max=100)),
        'national_id': fields.Str(required=True, validate=validate.Length(max=50))
    }, required=True)