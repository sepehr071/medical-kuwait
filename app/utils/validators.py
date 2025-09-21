import re
from marshmallow import Schema, fields, validate, ValidationError

# Phone number patterns for Kuwait and Germany
PHONE_PATTERNS = {
    'kuwait': [
        r'^\+965[56789]\d{7}$',      # +965XXXXXXXX
        r'^965[56789]\d{7}$',        # 965XXXXXXXX
        r'^[56789]\d{7}$'            # 8-digit local
    ],
    'germany': [
        r'^\+49[1-9]\d{8,11}$',      # +49XXXXXXXXX (9-12 digits after +49)
        r'^49[1-9]\d{8,11}$',        # 49XXXXXXXXX
        r'^0[1-9]\d{8,10}$'          # 0XXXXXXXXX (German local format)
    ]
}

def validate_international_phone(phone: str) -> str:
    """
    Validate and normalize Kuwait or German phone number
    
    Args:
        phone (str): Phone number to validate
        
    Returns:
        str: Normalized phone number in international format
        
    Raises:
        ValidationError: If phone number is invalid
    """
    if not phone:
        raise ValidationError("Phone number is required")
    
    # Remove spaces and special chars except +
    cleaned = re.sub(r'[^\d+]', '', str(phone))
    
    # Check Kuwait patterns first
    for pattern in PHONE_PATTERNS['kuwait']:
        if re.match(pattern, cleaned):
            if cleaned.startswith('+965'):
                return cleaned
            elif cleaned.startswith('965'):
                return '+' + cleaned
            else:  # 8-digit local
                return '+965' + cleaned
    
    # Check German patterns
    for pattern in PHONE_PATTERNS['germany']:
        if re.match(pattern, cleaned):
            if cleaned.startswith('+49'):
                return cleaned
            elif cleaned.startswith('49'):
                return '+' + cleaned
            elif cleaned.startswith('0'):  # German local format
                return '+49' + cleaned[1:]  # Remove leading 0 and add +49
    
    raise ValidationError("Invalid phone number format. Must be Kuwait (+965) or German (+49) phone number")

# Keep old function name for backward compatibility
def validate_kuwait_phone(phone: str) -> str:
    """Backward compatibility wrapper"""
    return validate_international_phone(phone)

# Custom field for international phone validation (Kuwait and Germany)
class InternationalPhoneField(fields.String):
    """Custom marshmallow field for Kuwait and German phone validation"""
    
    def _deserialize(self, value, attr, data, **kwargs):
        value = super()._deserialize(value, attr, data, **kwargs)
        if value:
            return validate_international_phone(value)
        return value

# Keep old field name for backward compatibility
class KuwaitPhoneField(InternationalPhoneField):
    """Backward compatibility wrapper"""
    pass

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