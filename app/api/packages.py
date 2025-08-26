from flask import Blueprint, request
from app.services.package_service import PackageService
from app.utils.validators import PurchasePackageSchema
from app.utils.decorators import jwt_required_with_user, validate_json_schema, handle_exceptions
from app.utils.helpers import success_response, error_response

packages_bp = Blueprint('packages', __name__)

@packages_bp.route('/available', methods=['GET'])
@handle_exceptions
def get_available_packages():
    """
    Get currently available package for purchase
    
    GET /api/packages/available
    """
    package_service = PackageService()
    package_data = package_service.get_available_package()
    
    if package_data:
        return success_response(
            {"package": package_data}, 
            "Available package retrieved successfully"
        )
    else:
        return error_response(
            "NO_PACKAGES_AVAILABLE", 
            "No packages available for purchase", 
            status_code=404
        )

@packages_bp.route('/purchase', methods=['POST'])
@jwt_required_with_user()
@validate_json_schema(PurchasePackageSchema)
@handle_exceptions
def purchase_package():
    """
    Purchase a package for authenticated user
    
    POST /api/packages/purchase
    Headers: Authorization: Bearer <jwt_token>
    {
        "package_id": "uuid",
        "user_info": {
            "name": "string",
            "national_id": "string"
        }
    }
    """
    user = request.current_user
    data = request.validated_data
    
    package_id = data['package_id']
    user_info = data['user_info']
    
    package_service = PackageService()
    
    success, message, subscription_data = package_service.purchase_package(
        user_id=user.user_id,
        package_id=package_id,
        user_info=user_info
    )
    
    if success:
        return success_response(
            {"subscription": subscription_data}, 
            message
        )
    else:
        if "already has" in message.lower():
            error_code = "ACTIVE_PACKAGE_EXISTS"
        elif "not found" in message.lower():
            error_code = "PACKAGE_NOT_FOUND"
        elif "not available" in message.lower():
            error_code = "PACKAGE_UNAVAILABLE"
        else:
            error_code = "PURCHASE_FAILED"
        
        return error_response(error_code, message, status_code=400)

@packages_bp.route('/history', methods=['GET'])
@jwt_required_with_user()
@handle_exceptions
def get_package_history():
    """
    Get package purchase history for current user
    
    GET /api/packages/history
    Headers: Authorization: Bearer <jwt_token>
    """
    user = request.current_user
    package_service = PackageService()
    
    history = package_service.get_user_package_history(user.user_id)
    
    return success_response(
        {"history": history}, 
        "Package history retrieved successfully"
    )

@packages_bp.route('/subscription/<subscription_id>/status', methods=['PUT'])
@jwt_required_with_user()
@handle_exceptions
def update_subscription_status(subscription_id):
    """
    Update payment status for a subscription (for admin use or payment webhook)
    
    PUT /api/packages/subscription/<subscription_id>/status
    Headers: Authorization: Bearer <jwt_token>
    {
        "payment_status": "completed|failed|pending"
    }
    """
    if not request.is_json:
        return error_response("INVALID_REQUEST", "Request must be JSON", status_code=400)
    
    data = request.get_json()
    if not data or 'payment_status' not in data:
        return error_response("INVALID_REQUEST", "payment_status is required", status_code=400)
    
    payment_status = data['payment_status']
    
    if payment_status not in ['completed', 'failed', 'pending']:
        return error_response(
            "INVALID_STATUS", 
            "payment_status must be one of: completed, failed, pending", 
            status_code=400
        )
    
    package_service = PackageService()
    success = package_service.update_payment_status(subscription_id, payment_status)
    
    if success:
        return success_response(
            {"subscription_id": subscription_id, "payment_status": payment_status}, 
            "Payment status updated successfully"
        )
    else:
        return error_response(
            "UPDATE_FAILED", 
            "Failed to update payment status", 
            status_code=400
        )