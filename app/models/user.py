from datetime import datetime
from app.config.database import get_db
from app.utils.helpers import generate_uuid, calculate_remaining_days, serialize_datetime

class User:
    def __init__(self, phone_number, name=None, national_id=None, user_id=None, 
                 is_active=True, created_at=None, updated_at=None, active_package=None):
        self.user_id = user_id or generate_uuid()
        self.phone_number = phone_number
        self.name = name
        self.national_id = national_id
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.active_package = active_package

    def to_dict(self, include_active_package=True):
        """Convert user to dictionary"""
        user_dict = {
            "user_id": self.user_id,
            "phone_number": self.phone_number,
            "name": self.name,
            "national_id": self.national_id,
            "is_active": self.is_active,
            "created_at": serialize_datetime(self.created_at),
            "updated_at": serialize_datetime(self.updated_at)
        }
        
        if include_active_package and self.active_package:
            # Calculate remaining days for active package
            if self.active_package.get('expires_at'):
                remaining_days = calculate_remaining_days(self.active_package['expires_at'])
                active_package_dict = self.active_package.copy()
                active_package_dict['remaining_days'] = remaining_days
                active_package_dict['expires_at'] = serialize_datetime(active_package_dict['expires_at'])
                active_package_dict['purchased_at'] = serialize_datetime(active_package_dict['purchased_at'])
                user_dict['active_package'] = active_package_dict
            else:
                user_dict['active_package'] = None
        
        return user_dict

    def save(self):
        """Save user to database"""
        db = get_db()
        self.updated_at = datetime.utcnow()
        
        user_data = {
            "user_id": self.user_id,
            "phone_number": self.phone_number,
            "name": self.name,
            "national_id": self.national_id,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "active_package": self.active_package
        }
        
        result = db.users.update_one(
            {"user_id": self.user_id},
            {"$set": user_data},
            upsert=True
        )
        return result

    @classmethod
    def find_by_phone(cls, phone_number):
        """Find user by phone number"""
        db = get_db()
        user_data = db.users.find_one({"phone_number": phone_number})
        if user_data:
            return cls.from_dict(user_data)
        return None

    @classmethod
    def find_by_id(cls, user_id):
        """Find user by user_id"""
        db = get_db()
        user_data = db.users.find_one({"user_id": user_id})
        if user_data:
            return cls.from_dict(user_data)
        return None

    @classmethod
    def from_dict(cls, data):
        """Create user from dictionary"""
        return cls(
            user_id=data.get('user_id'),
            phone_number=data.get('phone_number'),
            name=data.get('name'),
            national_id=data.get('national_id'),
            is_active=data.get('is_active', True),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            active_package=data.get('active_package')
        )

    def update_profile(self, name=None, national_id=None):
        """Update user profile"""
        if name is not None:
            self.name = name
        if national_id is not None:
            self.national_id = national_id
        return self.save()

    def update_phone(self, new_phone_number):
        """Update user phone number"""
        # Check if new phone is already taken
        existing_user = self.find_by_phone(new_phone_number)
        if existing_user and existing_user.user_id != self.user_id:
            raise ValueError("Phone number already exists")
        
        self.phone_number = new_phone_number
        return self.save()

    def set_active_package(self, package_data):
        """Set active package for user"""
        self.active_package = package_data
        return self.save()

    def has_active_package(self):
        """Check if user has active package"""
        if not self.active_package:
            return False
        
        expires_at = self.active_package.get('expires_at')
        if not expires_at:
            return False
        
        return expires_at > datetime.utcnow() and self.active_package.get('is_active', False)