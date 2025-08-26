#!/usr/bin/env python3
"""
Simple database initialization script that works with the Flask app
"""

import sys
import os
from datetime import datetime
import uuid

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.config.database import get_db

def init_sample_data():
    """Initialize sample data using Flask app context"""
    
    # Create Flask app
    app = create_app('development')
    
    with app.app_context():
        try:
            # Get database
            db = get_db()
            
            print("🔗 Connected to database successfully")
            
            # Check if packages already exist
            existing_packages = db.packages.count_documents({})
            print(f"📦 Found {existing_packages} existing packages")
            
            if existing_packages == 0:
                # Create sample packages
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
                
                # Insert packages
                for package in sample_packages:
                    db.packages.insert_one(package)
                    print(f"✅ Created package: {package['name']}")
                
                print(f"📦 Successfully created {len(sample_packages)} packages")
            else:
                print("📦 Packages already exist, skipping creation")
            
            # Show current packages
            active_packages = list(db.packages.find({"is_active": True}))
            print(f"🟢 Active packages: {len(active_packages)}")
            for pkg in active_packages:
                print(f"   - {pkg['name']}: ${pkg['price']} ({pkg['duration']} days)")
            
            # Show database stats
            users_count = db.users.count_documents({})
            otps_count = db.otp_codes.count_documents({})
            history_count = db.package_history.count_documents({})
            
            print(f"\n📊 Database Statistics:")
            print(f"   Users: {users_count}")
            print(f"   Packages: {db.packages.count_documents({})}")
            print(f"   OTP Codes: {otps_count}")
            print(f"   Package History: {history_count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error initializing data: {str(e)}")
            return False

if __name__ == "__main__":
    print("🏥 Kuwait Medical Clinic - Sample Data Initialization")
    print("=" * 55)
    
    success = init_sample_data()
    
    if success:
        print("\n✅ Sample data initialization completed successfully!")
    else:
        print("\n❌ Sample data initialization failed!")
        sys.exit(1)