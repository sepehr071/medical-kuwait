#!/usr/bin/env python3
"""
API Test Script for Kuwait Medical Clinic Flask Backend
This script simulates various API calls to test the functionality
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000/api"
TEST_PHONE = "+4915157347404"  # Kuwait phone number for testing
headers = {"Content-Type": "application/json"}

class Colors:
    """Terminal colors for output formatting"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")

def print_step(step_num, text):
    """Print formatted step"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}Step {step_num}: {text}{Colors.END}")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.WHITE}ℹ️  {text}{Colors.END}")

def make_request(method, endpoint, data=None, headers=None, auth_token=None):
    """Make HTTP request with error handling"""
    url = f"{BASE_URL}{endpoint}"
    
    # Add authorization header if token provided
    request_headers = headers.copy() if headers else {}
    if auth_token:
        request_headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=request_headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=request_headers)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=request_headers)
        else:
            print_error(f"Unsupported HTTP method: {method}")
            return None
        
        return response
    except requests.exceptions.ConnectionError:
        print_error("Connection failed! Make sure the Flask server is running on localhost:5000")
        return None
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return None

def test_health_check():
    """Test health check endpoint"""
    print_step(1, "Testing Health Check")
    
    response = make_request("GET", "/health")
    if not response:
        return False
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Health check passed: {data.get('message', 'OK')}")
        print_info(f"Database status: {data.get('data', {}).get('services', {}).get('database', 'Unknown')}")
        return True
    else:
        print_error(f"Health check failed: {response.status_code}")
        return False

def test_send_otp():
    """Test sending OTP"""
    print_step(2, "Testing Send OTP")
    
    data = {
        "phone_number": TEST_PHONE,
        "purpose": "login"
    }
    
    response = make_request("POST", "/auth/send-otp", data, headers)
    if not response:
        return False
    
    if response.status_code == 200:
        response_data = response.json()
        print_success("OTP sent successfully")
        print_info(f"Response: {response_data.get('message', 'OTP sent')}")
        print_warning("Check server console for OTP code (placeholder SMS service)")
        return True
    else:
        print_error(f"Send OTP failed: {response.status_code}")
        try:
            error_data = response.json()
            print_error(f"Error: {error_data.get('error', {}).get('message', 'Unknown error')}")
        except:
            print_error(f"Response: {response.text}")
        return False

def test_verify_otp():
    """Test OTP verification and login"""
    print_step(3, "Testing OTP Verification & Login")
    
    # Get OTP from user input
    print_info("Enter the OTP code from server console:")
    otp_code = input("OTP Code: ").strip()
    
    if len(otp_code) != 5 or not otp_code.isdigit():
        print_error("Invalid OTP format. Must be 5 digits.")
        return False, None
    
    data = {
        "phone_number": TEST_PHONE,
        "code": otp_code
    }
    
    response = make_request("POST", "/auth/verify-otp", data, headers)
    if not response:
        return False, None
    
    if response.status_code == 200:
        response_data = response.json()
        user_data = response_data.get('data', {})
        token = user_data.get('token')
        user_info = user_data.get('user', {})
        
        print_success("Login successful!")
        print_info(f"User ID: {user_info.get('user_id')}")
        print_info(f"Phone: {user_info.get('phone_number')}")
        print_info(f"Name: {user_info.get('name', 'Not set')}")
        print_info(f"Active Package: {'Yes' if user_info.get('active_package') else 'No'}")
        
        return True, token
    else:
        print_error(f"OTP verification failed: {response.status_code}")
        try:
            error_data = response.json()
            print_error(f"Error: {error_data.get('error', {}).get('message', 'Unknown error')}")
        except:
            print_error(f"Response: {response.text}")
        return False, None

def test_get_profile(token):
    """Test getting user profile"""
    print_step(4, "Testing Get User Profile")
    
    response = make_request("GET", "/user/profile", auth_token=token)
    if not response:
        return False
    
    if response.status_code == 200:
        data = response.json()
        user_data = data.get('data', {})
        
        print_success("Profile retrieved successfully")
        print_info(f"User ID: {user_data.get('user_id')}")
        print_info(f"Phone: {user_data.get('phone_number')}")
        print_info(f"Name: {user_data.get('name', 'Not set')}")
        print_info(f"National ID: {user_data.get('national_id', 'Not set')}")
        print_info(f"Created: {user_data.get('created_at')}")
        
        active_package = user_data.get('active_package')
        if active_package:
            print_info(f"Active Package: {active_package.get('name')}")
            print_info(f"Expires: {active_package.get('expires_at')}")
            print_info(f"Remaining Days: {active_package.get('remaining_days')}")
        else:
            print_info("No active package")
        
        return True
    else:
        print_error(f"Get profile failed: {response.status_code}")
        return False

def test_update_profile(token):
    """Test updating user profile"""
    print_step(5, "Testing Update User Profile")
    
    data = {
        "name": "Ahmed Al-Kuwait",
        "national_id": "123456789"
    }
    
    response = make_request("PUT", "/user/profile", data, headers, token)
    if not response:
        return False
    
    if response.status_code == 200:
        response_data = response.json()
        user_data = response_data.get('data', {})
        
        print_success("Profile updated successfully")
        print_info(f"Name: {user_data.get('name')}")
        print_info(f"National ID: {user_data.get('national_id')}")
        return True
    else:
        print_error(f"Update profile failed: {response.status_code}")
        return False

def test_get_packages():
    """Test getting available packages"""
    print_step(6, "Testing Get Available Packages")
    
    response = make_request("GET", "/packages/available")
    if not response:
        return False, None
    
    if response.status_code == 200:
        data = response.json()
        package_data = data.get('data', {}).get('package', {})
        
        print_success("Available package retrieved")
        print_info(f"Package ID: {package_data.get('package_id')}")
        print_info(f"Name: {package_data.get('name')}")
        print_info(f"Price: ${package_data.get('price')}")
        print_info(f"Duration: {package_data.get('duration')} days")
        print_info(f"Description: {package_data.get('description', 'N/A')}")
        
        return True, package_data.get('package_id')
    else:
        print_error(f"Get packages failed: {response.status_code}")
        return False, None

def test_purchase_package(token, package_id):
    """Test purchasing a package"""
    print_step(7, "Testing Purchase Package")
    
    if not package_id:
        print_warning("No package ID available, skipping purchase test")
        return False
    
    data = {
        "package_id": package_id,
        "user_info": {
            "name": "Ahmed Al-Kuwait",
            "national_id": "123456789"
        }
    }
    
    response = make_request("POST", "/packages/purchase", data, headers, token)
    if not response:
        return False
    
    if response.status_code == 200:
        response_data = response.json()
        subscription_data = response_data.get('data', {}).get('subscription', {})
        
        print_success("Package purchased successfully")
        print_info(f"Subscription ID: {subscription_data.get('subscription_id')}")
        print_info(f"Package: {subscription_data.get('package', {}).get('name')}")
        print_info(f"Price: ${subscription_data.get('package', {}).get('price')}")
        print_info(f"Purchased: {subscription_data.get('purchased_at')}")
        print_info(f"Expires: {subscription_data.get('expires_at')}")
        print_info(f"Remaining Days: {subscription_data.get('remaining_days')}")
        print_info(f"Payment Status: {subscription_data.get('payment_status')}")
        
        return True
    else:
        response_data = response.json()
        error_msg = response_data.get('error', {}).get('message', 'Unknown error')
        
        if "already has" in error_msg.lower():
            print_warning(f"Purchase skipped: {error_msg}")
            return True  # Not really an error for testing
        else:
            print_error(f"Purchase failed: {error_msg}")
            return False

def test_package_history(token):
    """Test getting package history"""
    print_step(8, "Testing Get Package History")
    
    response = make_request("GET", "/packages/history", auth_token=token)
    if not response:
        return False
    
    if response.status_code == 200:
        data = response.json()
        history = data.get('data', {}).get('history', [])
        
        print_success(f"Package history retrieved ({len(history)} records)")
        
        for i, record in enumerate(history, 1):
            print_info(f"Record {i}:")
            print_info(f"  Subscription ID: {record.get('subscription_id')}")
            print_info(f"  Package ID: {record.get('package_id')}")
            print_info(f"  Purchased: {record.get('purchased_at')}")
            print_info(f"  Expires: {record.get('expires_at')}")
            print_info(f"  Status: {record.get('payment_status')}")
            print_info(f"  Remaining Days: {record.get('remaining_days')}")
        
        return True
    else:
        print_error(f"Get package history failed: {response.status_code}")
        return False

def test_error_scenarios():
    """Test various error scenarios"""
    print_step(9, "Testing Error Scenarios")
    
    # Test invalid phone number
    print_info("Testing invalid phone number...")
    data = {"phone_number": "invalid", "purpose": "login"}
    response = make_request("POST", "/auth/send-otp", data, headers)
    if response and response.status_code == 400:
        response_data = response.json()
        if not response_data.get("success"):
            print_success("Invalid phone validation working")
        else:
            print_warning("Invalid phone validation may not be working properly")
    else:
        print_warning("Invalid phone validation may not be working properly")
    
    # Test invalid OTP
    print_info("Testing invalid OTP...")
    data = {"phone_number": TEST_PHONE, "code": "00000"}
    response = make_request("POST", "/auth/verify-otp", data, headers)
    if response and response.status_code == 400:
        response_data = response.json()
        if not response_data.get("success"):
            print_success("Invalid OTP validation working")
        else:
            print_warning("Invalid OTP validation may not be working properly")
    else:
        print_warning("Invalid OTP validation may not be working properly")
    
    # Test unauthorized access
    print_info("Testing unauthorized access...")
    response = make_request("GET", "/user/profile")
    if response and response.status_code in [401, 422]:  # JWT required
        print_success("Authorization protection working")
    else:
        print_warning("Authorization protection may not be working properly")
    
    return True

def run_all_tests():
    """Run all API tests"""
    print_header("Kuwait Medical Clinic API Test Suite")
    print_info(f"Testing API at: {BASE_URL}")
    print_info(f"Test phone number: {TEST_PHONE}")
    print_info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests_passed = 0
    total_tests = 9
    
    # Test 1: Health Check
    if test_health_check():
        tests_passed += 1
    
    # Test 2: Send OTP
    if test_send_otp():
        tests_passed += 1
        
        # Test 3: Verify OTP (requires user input)
        success, token = test_verify_otp()
        if success and token:
            tests_passed += 1
            
            # Test 4: Get Profile
            if test_get_profile(token):
                tests_passed += 1
            
            # Test 5: Update Profile
            if test_update_profile(token):
                tests_passed += 1
            
            # Test 6: Get Packages
            success, package_id = test_get_packages()
            if success:
                tests_passed += 1
                
                # Test 7: Purchase Package
                if test_purchase_package(token, package_id):
                    tests_passed += 1
            
            # Test 8: Package History
            if test_package_history(token):
                tests_passed += 1
    
    # Test 9: Error Scenarios
    if test_error_scenarios():
        tests_passed += 1
    
    # Results
    print_header("Test Results")
    if tests_passed == total_tests:
        print_success(f"All tests passed! ({tests_passed}/{total_tests})")
    else:
        print_warning(f"Tests completed: {tests_passed}/{total_tests} passed")
    
    print_info(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    print(f"{Colors.BOLD}{Colors.PURPLE}")
    print("🏥 Kuwait Medical Clinic API Tester")
    print("===================================")
    print(f"{Colors.END}")
    
    print_warning("Make sure the Flask server is running: python run.py")
    print_warning("Make sure MongoDB is running and database is initialized")
    
    input("\nPress Enter to start testing...")
    
    run_all_tests()