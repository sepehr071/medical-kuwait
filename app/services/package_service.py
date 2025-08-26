from datetime import datetime
from flask import current_app
from app.models.package import Package
from app.models.user import User
from app.models.package_history import PackageHistory
from app.utils.helpers import calculate_package_expiry, calculate_remaining_days

class PackageService:
    """Service for package management and subscription operations"""
    
    def get_available_package(self):
        """
        Get the available package for purchase
        Assuming single package system as per specification
        
        Returns:
            dict: Package data or None
        """
        try:
            package = Package.get_active_package()
            if package:
                return package.to_dict()
            return None
        except Exception as e:
            current_app.logger.error(f"Error getting available package: {str(e)}")
            return None
    
    def purchase_package(self, user_id, package_id, user_info):
        """
        Purchase a package for a user
        
        Args:
            user_id (str): User ID
            package_id (str): Package ID to purchase
            user_info (dict): User information to update (name, national_id)
            
        Returns:
            tuple: (success, message, subscription_data)
        """
        try:
            # Get user
            user = User.find_by_id(user_id)
            if not user:
                return False, "User not found", None
            
            # Check if user already has active package
            if user.has_active_package():
                return False, "User already has an active package", None
            
            # Get package
            package = Package.find_by_id(package_id)
            if not package:
                return False, "Package not found", None
            
            if not package.is_active:
                return False, "Package is not available for purchase", None
            
            # Update user profile with provided information
            user.update_profile(
                name=user_info.get('name'),
                national_id=user_info.get('national_id')
            )
            
            # Calculate expiry date
            expires_at = calculate_package_expiry(package.duration)
            
            # Create package history record
            package_history = PackageHistory(
                user_id=user_id,
                package_id=package_id,
                expires_at=expires_at,
                payment_status='pending',  # Start as pending
                is_active=True
            )
            package_history.save()
            
            # Set active package for user
            active_package_data = {
                "package_id": package.package_id,
                "name": package.name,
                "price": package.price,
                "purchased_at": package_history.purchased_at,
                "expires_at": expires_at,
                "payment_status": "pending",
                "is_active": True
            }
            user.set_active_package(active_package_data)
            
            # Prepare response data
            subscription_data = {
                "subscription_id": package_history.subscription_id,
                "package": {
                    "name": package.name,
                    "price": package.price,
                    "duration": package.duration
                },
                "purchased_at": package_history.purchased_at.isoformat() + 'Z',
                "expires_at": expires_at.isoformat() + 'Z',
                "remaining_days": calculate_remaining_days(expires_at),
                "payment_status": "pending"
            }
            
            return True, "Package purchased successfully", subscription_data
            
        except Exception as e:
            current_app.logger.error(f"Error purchasing package: {str(e)}")
            return False, str(e), None
    
    def update_payment_status(self, subscription_id, status):
        """
        Update payment status for a subscription
        
        Args:
            subscription_id (str): Subscription ID
            status (str): New payment status (pending, completed, failed)
            
        Returns:
            bool: Success status
        """
        try:
            # Update package history
            package_history = PackageHistory.find_by_id(subscription_id)
            if not package_history:
                return False
            
            package_history.update_payment_status(status)
            
            # Update user's active package status if needed
            user = User.find_by_id(package_history.user_id)
            if user and user.active_package:
                user.active_package['payment_status'] = status
                user.save()
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error updating payment status: {str(e)}")
            return False
    
    def get_user_package_history(self, user_id):
        """
        Get package purchase history for a user
        
        Args:
            user_id (str): User ID
            
        Returns:
            list: List of package history records
        """
        try:
            history_list = PackageHistory.find_by_user(user_id)
            return [history.to_dict() for history in history_list]
        except Exception as e:
            current_app.logger.error(f"Error getting package history: {str(e)}")
            return []
    
    def check_and_expire_packages(self):
        """
        Check for expired packages and mark them as inactive
        This could be run as a background task
        
        Returns:
            int: Number of packages expired
        """
        try:
            from app.config.database import get_db
            db = get_db()
            
            # Find users with expired active packages
            expired_count = 0
            users_with_expired = db.users.find({
                "active_package.expires_at": {"$lt": datetime.utcnow()},
                "active_package.is_active": True
            })
            
            for user_data in users_with_expired:
                user = User.from_dict(user_data)
                if user.active_package:
                    user.active_package['is_active'] = False
                    user.save()
                    expired_count += 1
            
            return expired_count
            
        except Exception as e:
            current_app.logger.error(f"Error checking expired packages: {str(e)}")
            return 0