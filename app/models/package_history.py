from datetime import datetime
from app.config.database import get_db
from app.utils.helpers import generate_uuid, serialize_datetime, calculate_remaining_days

class PackageHistory:
    def __init__(self, user_id, package_id, purchased_at=None, expires_at=None,
                 payment_status='pending', is_active=True, subscription_id=None):
        self.subscription_id = subscription_id or generate_uuid()
        self.user_id = user_id
        self.package_id = package_id
        self.purchased_at = purchased_at or datetime.utcnow()
        self.expires_at = expires_at
        self.payment_status = payment_status  # pending, completed, failed
        self.is_active = is_active

    def to_dict(self):
        """Convert package history to dictionary"""
        return {
            "subscription_id": self.subscription_id,
            "user_id": self.user_id,
            "package_id": self.package_id,
            "purchased_at": serialize_datetime(self.purchased_at),
            "expires_at": serialize_datetime(self.expires_at),
            "payment_status": self.payment_status,
            "is_active": self.is_active,
            "remaining_days": calculate_remaining_days(self.expires_at) if self.expires_at else 0
        }

    def save(self):
        """Save package history to database"""
        db = get_db()
        
        history_data = {
            "subscription_id": self.subscription_id,
            "user_id": self.user_id,
            "package_id": self.package_id,
            "purchased_at": self.purchased_at,
            "expires_at": self.expires_at,
            "payment_status": self.payment_status,
            "is_active": self.is_active
        }
        
        result = db.package_history.update_one(
            {"subscription_id": self.subscription_id},
            {"$set": history_data},
            upsert=True
        )
        return result

    @classmethod
    def find_by_user(cls, user_id):
        """Find all package history for a user"""
        db = get_db()
        history_list = []
        for history_data in db.package_history.find({"user_id": user_id}).sort("purchased_at", -1):
            history_list.append(cls.from_dict(history_data))
        return history_list

    @classmethod
    def find_by_id(cls, subscription_id):
        """Find package history by subscription_id"""
        db = get_db()
        history_data = db.package_history.find_one({"subscription_id": subscription_id})
        if history_data:
            return cls.from_dict(history_data)
        return None

    @classmethod
    def from_dict(cls, data):
        """Create package history from dictionary"""
        return cls(
            subscription_id=data.get('subscription_id'),
            user_id=data.get('user_id'),
            package_id=data.get('package_id'),
            purchased_at=data.get('purchased_at'),
            expires_at=data.get('expires_at'),
            payment_status=data.get('payment_status', 'pending'),
            is_active=data.get('is_active', True)
        )

    def update_payment_status(self, status):
        """Update payment status"""
        self.payment_status = status
        return self.save()

    def deactivate(self):
        """Deactivate subscription"""
        self.is_active = False
        return self.save()