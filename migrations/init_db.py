import sys
import os
from datetime import datetime
import uuid

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
from app.config.database import create_indexes
from app.models.package import Package
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_database():
    """Initialize MongoDB with indexes and sample data"""
    
    try:
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017')
        db = client['kuwait_medical_clinic']
        
        logger.info("Connected to MongoDB successfully")
        
        # Test connection
        db.command('ping')
        logger.info("Database connection verified")
        
        # Clear existing data (for fresh setup)
        clear_existing_data = input("Clear existing data? (y/N): ").lower().strip()
        if clear_existing_data == 'y':
            logger.info("Clearing existing collections...")
            db.users.delete_many({})
            db.packages.delete_many({})
            db.otp_codes.delete_many({})
            db.package_history.delete_many({})
            logger.info("Existing data cleared")
        
        # Create indexes
        logger.info("Creating database indexes...")
        
        # Users collection indexes
        users = db.users
        users.create_index("phone_number", unique=True)
        users.create_index("user_id", unique=True)
        users.create_index("is_active")
        logger.info("Users collection indexes created")
        
        # Packages collection indexes  
        packages = db.packages
        packages.create_index("package_id", unique=True)
        packages.create_index("is_active")
        logger.info("Packages collection indexes created")
        
        # OTP codes collection with TTL index
        otp_codes = db.otp_codes
        otp_codes.create_index("phone_number")
        otp_codes.create_index("expires_at", expireAfterSeconds=0)  # TTL index
        otp_codes.create_index("otp_id", unique=True)
        logger.info("OTP codes collection indexes created")
        
        # Package history collection
        package_history = db.package_history
        package_history.create_index("user_id")
        package_history.create_index("subscription_id", unique=True)
        logger.info("Package history collection indexes created")
        
        # Insert sample packages
        logger.info("Creating sample packages...")
        
        sample_packages = [
            {
                "package_id": str(uuid.uuid4()),
                "name": "Basic Medical Package",
                "price": 50.0,
                "duration": 30,  # 30 days
                "description": "Basic medical consultation package with 30-day access",
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "package_id": str(uuid.uuid4()),
                "name": "Premium Medical Package",
                "price": 100.0,
                "duration": 90,  # 90 days
                "description": "Premium medical consultation package with 90-day access",
                "is_active": False,  # Not active by default
                "created_at": datetime.utcnow()
            }
        ]
        
        for package_data in sample_packages:
            existing = packages.find_one({"name": package_data["name"]})
            if not existing:
                packages.insert_one(package_data)
                logger.info(f"Created package: {package_data['name']}")
            else:
                logger.info(f"Package already exists: {package_data['name']}")
        
        # Display summary
        logger.info("\n" + "="*50)
        logger.info("DATABASE INITIALIZATION COMPLETE")
        logger.info("="*50)
        
        # Show collection counts
        users_count = db.users.count_documents({})
        packages_count = db.packages.count_documents({})
        active_packages_count = db.packages.count_documents({"is_active": True})
        otp_count = db.otp_codes.count_documents({})
        history_count = db.package_history.count_documents({})
        
        logger.info(f"Users: {users_count}")
        logger.info(f"Packages: {packages_count} (Active: {active_packages_count})")
        logger.info(f"OTP Codes: {otp_count}")
        logger.info(f"Package History: {history_count}")
        
        # List active packages
        logger.info("\nActive Packages:")
        for package in db.packages.find({"is_active": True}):
            logger.info(f"  - {package['name']}: ${package['price']} ({package['duration']} days)")
        
        logger.info(f"\nDatabase: {db.name}")
        logger.info(f"Connection: {client.address}")
        logger.info("="*50)
        
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return False
    finally:
        if 'client' in locals():
            client.close()

def reset_database():
    """Reset database - drop all collections"""
    try:
        client = MongoClient('mongodb://localhost:27017')
        db = client['kuwait_medical_clinic']
        
        confirm = input("This will delete ALL data. Are you sure? Type 'DELETE' to confirm: ")
        if confirm != 'DELETE':
            logger.info("Reset cancelled")
            return False
        
        # Drop all collections
        collections = db.list_collection_names()
        for collection in collections:
            db[collection].drop()
            logger.info(f"Dropped collection: {collection}")
        
        logger.info("Database reset complete")
        return True
        
    except Exception as e:
        logger.error(f"Database reset failed: {str(e)}")
        return False
    finally:
        if 'client' in locals():
            client.close()

def check_database_status():
    """Check database connection and status"""
    try:
        client = MongoClient('mongodb://localhost:27017')
        db = client['kuwait_medical_clinic']
        
        # Test connection
        db.command('ping')
        
        logger.info("Database Status:")
        logger.info(f"Connection: OK")
        logger.info(f"Database: {db.name}")
        
        # Collection counts
        collections = ['users', 'packages', 'otp_codes', 'package_history']
        for collection in collections:
            count = db[collection].count_documents({})
            logger.info(f"{collection}: {count} documents")
        
        # Active packages
        active_packages = db.packages.count_documents({"is_active": True})
        logger.info(f"Active packages: {active_packages}")
        
        return True
        
    except Exception as e:
        logger.error(f"Database check failed: {str(e)}")
        return False
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Database management script')
    parser.add_argument('action', choices=['init', 'reset', 'status'], 
                       help='Action to perform')
    
    args = parser.parse_args()
    
    if args.action == 'init':
        success = initialize_database()
        sys.exit(0 if success else 1)
    elif args.action == 'reset':
        success = reset_database()
        sys.exit(0 if success else 1)
    elif args.action == 'status':
        success = check_database_status()
        sys.exit(0 if success else 1)