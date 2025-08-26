from datetime import datetime
from app.config.database import get_db
from app.utils.helpers import generate_uuid, get_otp_expiry, hash_otp, verify_otp

class OTPCode:
    def __init__(self, phone_number, code, purpose, user_id=None, otp_id=None,
                 created_at=None, expires_at=None, is_used=False):
        self.otp_id = otp_id or generate_uuid()
        self.phone_number = phone_number
        self.code_hash = hash_otp(code) if not code.startswith('$2b$') else code  # Check if already hashed
        self.purpose = purpose  # 'login' or 'phone_change'
        self.user_id = user_id
        self.created_at = created_at or datetime.utcnow()
        self.expires_at = expires_at or get_otp_expiry()
        self.is_used = is_used

    def to_dict(self, include_code=False):
        """Convert OTP to dictionary"""
        otp_dict = {
            "otp_id": self.otp_id,
            "phone_number": self.phone_number,
            "purpose": self.purpose,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "is_used": self.is_used
        }
        
        if include_code:
            otp_dict["code_hash"] = self.code_hash
        
        return otp_dict

    def save(self):
        """Save OTP to database"""
        db = get_db()
        
        otp_data = {
            "otp_id": self.otp_id,
            "phone_number": self.phone_number,
            "code_hash": self.code_hash,
            "purpose": self.purpose,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "is_used": self.is_used
        }
        
        result = db.otp_codes.update_one(
            {"otp_id": self.otp_id},
            {"$set": otp_data},
            upsert=True
        )
        return result

    @classmethod
    def find_by_phone_and_purpose(cls, phone_number, purpose):
        """Find latest valid OTP by phone and purpose"""
        db = get_db()
        otp_data = db.otp_codes.find_one(
            {
                "phone_number": phone_number,
                "purpose": purpose,
                "is_used": False,
                "expires_at": {"$gt": datetime.utcnow()}
            },
            sort=[("created_at", -1)]  # Get latest OTP
        )
        if otp_data:
            return cls.from_dict(otp_data)
        return None

    @classmethod
    def from_dict(cls, data):
        """Create OTP from dictionary"""
        return cls(
            otp_id=data.get('otp_id'),
            phone_number=data.get('phone_number'),
            code=data.get('code_hash'),  # Already hashed
            purpose=data.get('purpose'),
            user_id=data.get('user_id'),
            created_at=data.get('created_at'),
            expires_at=data.get('expires_at'),
            is_used=data.get('is_used', False)
        )

    def verify(self, plain_code):
        """Verify OTP code"""
        # Check if OTP is expired
        if datetime.utcnow() > self.expires_at:
            return False, "OTP has expired"
        
        # Check if OTP is already used
        if self.is_used:
            return False, "OTP has already been used"
        
        # Verify the code
        if verify_otp(plain_code, self.code_hash):
            return True, "OTP verified successfully"
        else:
            return False, "Invalid OTP code"

    def mark_as_used(self):
        """Mark OTP as used"""
        self.is_used = True
        return self.save()

    def is_expired(self):
        """Check if OTP is expired"""
        return datetime.utcnow() > self.expires_at

    @classmethod
    def cleanup_expired(cls):
        """Clean up expired OTP codes (this will be handled by TTL index in MongoDB)"""
        db = get_db()
        result = db.otp_codes.delete_many({
            "expires_at": {"$lt": datetime.utcnow()}
        })
        return result.deleted_count

    @classmethod
    def invalidate_previous_otps(cls, phone_number, purpose):
        """Invalidate all previous OTPs for phone and purpose"""
        db = get_db()
        result = db.otp_codes.update_many(
            {
                "phone_number": phone_number,
                "purpose": purpose,
                "is_used": False
            },
            {"$set": {"is_used": True}}
        )
        return result.modified_count