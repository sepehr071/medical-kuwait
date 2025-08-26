from datetime import datetime
from app.config.database import get_db
from app.utils.helpers import generate_uuid, serialize_datetime

class Package:
    def __init__(self, name, price, duration, description=None, package_id=None, 
                 is_active=True, created_at=None):
        self.package_id = package_id or generate_uuid()
        self.name = name
        self.price = float(price)
        self.duration = int(duration)  # duration in days
        self.description = description
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self):
        """Convert package to dictionary"""
        return {
            "package_id": self.package_id,
            "name": self.name,
            "price": self.price,
            "duration": self.duration,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": serialize_datetime(self.created_at)
        }

    def save(self):
        """Save package to database"""
        db = get_db()
        
        package_data = {
            "package_id": self.package_id,
            "name": self.name,
            "price": self.price,
            "duration": self.duration,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at
        }
        
        result = db.packages.update_one(
            {"package_id": self.package_id},
            {"$set": package_data},
            upsert=True
        )
        return result

    @classmethod
    def find_by_id(cls, package_id):
        """Find package by package_id"""
        db = get_db()
        package_data = db.packages.find_one({"package_id": package_id})
        if package_data:
            return cls.from_dict(package_data)
        return None

    @classmethod
    def get_active_package(cls):
        """Get the first active package (assuming single package system)"""
        db = get_db()
        package_data = db.packages.find_one({"is_active": True})
        if package_data:
            return cls.from_dict(package_data)
        return None

    @classmethod
    def get_all_active(cls):
        """Get all active packages"""
        db = get_db()
        packages = []
        for package_data in db.packages.find({"is_active": True}):
            packages.append(cls.from_dict(package_data))
        return packages

    @classmethod
    def from_dict(cls, data):
        """Create package from dictionary"""
        return cls(
            package_id=data.get('package_id'),
            name=data.get('name'),
            price=data.get('price'),
            duration=data.get('duration'),
            description=data.get('description'),
            is_active=data.get('is_active', True),
            created_at=data.get('created_at')
        )

    def deactivate(self):
        """Deactivate package"""
        self.is_active = False
        return self.save()

    def activate(self):
        """Activate package"""
        self.is_active = True
        return self.save()