from pymongo import MongoClient
from flask import current_app, g
import logging

# Global database connection
_db = None

def init_db(app):
    """Initialize database connection"""
    global _db
    try:
        client = MongoClient(app.config['MONGODB_URI'])
        _db = client[app.config['MONGODB_DB_NAME']]
        
        # Test connection
        _db.command('ping')
        app.logger.info(f"Connected to MongoDB: {app.config['MONGODB_DB_NAME']}")
        
        # Create indexes
        create_indexes()
        
    except Exception as e:
        app.logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise

def get_db():
    """Get database instance"""
    global _db
    if _db is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _db

def create_indexes():
    """Create database indexes"""
    db = get_db()
    
    try:
        # Users collection indexes
        users = db.users
        users.create_index("phone_number", unique=True)
        users.create_index("user_id", unique=True)
        users.create_index("is_active")
        
        # Packages collection indexes
        packages = db.packages
        packages.create_index("package_id", unique=True)
        packages.create_index("is_active")
        
        # OTP codes collection with TTL index
        otp_codes = db.otp_codes
        otp_codes.create_index("phone_number")
        otp_codes.create_index("expires_at", expireAfterSeconds=0)  # TTL index
        otp_codes.create_index("otp_id", unique=True)
        
        # Package history collection
        package_history = db.package_history
        package_history.create_index("user_id")
        package_history.create_index("subscription_id", unique=True)
        
        logging.info("Database indexes created successfully")
        
    except Exception as e:
        logging.error(f"Error creating indexes: {str(e)}")
        raise

def close_db():
    """Close database connection"""
    global _db
    if _db is not None:
        _db.client.close()
        _db = None