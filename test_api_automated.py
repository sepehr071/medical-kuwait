#!/usr/bin/env python3
"""
Automated API Test Script for Kuwait Medical Clinic Flask Backend
This script runs automated tests without requiring manual OTP input
"""

import requests
import json
import time
import re
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000/api"
TEST_PHONE = "+96551234567"
headers = {"Content-Type": "application/json"}

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def add_result(self, test_name, success, message=""):
        self.results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        if success:
            self.passed += 1
        else:
            self.failed += 1
    
    def print_summary(self):
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests: {self.passed + self.failed}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success Rate: {(self.passed/(self.passed+self.failed)*100):.1f}%")
        
        if self.failed > 0:
            print(f"\nFailed Tests:")
            for result in self.results:
                if not result["success"]:
                    print(f"  ❌ {result['test']}: {result['message']}")

def make_request(method, endpoint, data=None, headers=None, auth_token=None):
    """Make HTTP request with error handling"""
    url = f"{BASE_URL}{endpoint}"
    
    request_headers = headers.copy() if headers else {}
    if auth_token:
        request_headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=request_headers, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=request_headers, timeout=10)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=request_headers, timeout=10)
        else:
            return None
        
        return response
    except requests.exceptions.ConnectionError:
        return None
    except Exception as e:
        return None

def extract_otp_from_logs():
    """
    Extract OTP from server logs (placeholder implementation)
    In a real scenario, you might read from log files or use a test SMS service
    """
    # For testing purposes, we'll use a known test OTP
    # In production, this would be replaced with actual log parsing
    return "12345"

def test_health_check(results):
    """Test health check endpoint"""
    print("Testing health check...")
    
    response = make_request("GET", "/health")
    if not response:
        results.add_result("Health Check", False, "Connection failed")
        return False
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success") and "healthy" in data.get("data", {}).get("status", ""):
            results.add_result("Health Check", True, "API is healthy")
            return True
    
    results.add_result("Health Check", False, f"Status: {response.status_code}")
    return False

def test_send_otp(results):
    """Test sending OTP"""
    print("Testing send OTP...")
    
    data = {
        "phone_number": TEST_PHONE,
        "purpose": "login"
    }
    
    response = make_request("POST", "/auth/send-otp", data, headers)
    if not response:
        results.add_result("Send OTP", False, "Connection failed")
        return False
    
    if response.status_code == 200:
        response_data = response.json()
        if response_data.get("success"):
            results.add_result("Send OTP", True, "OTP sent successfully")
            return True
    
    results.add_result("Send OTP", False, f"Status: {response.status_code}")
    return False

def test_verify_otp_with_mock(results):
    """Test OTP verification with mock OTP"""
    print("Testing OTP verification...")
    
    # For automated testing, we'll test with an invalid OTP first
    # to verify the validation is working
    data = {
        "phone_number": TEST_PHONE,
        "code": "00000"  # Invalid OTP
    }
    
    response = make_request("POST", "/auth/verify-otp", data, headers)
    if not response:
        results.add_result("OTP Validation", False, "Connection failed")
        return False, None
    
    if response.status_code == 400:
        response_data = response.json()
        if not response_data.get("success"):
            results.add_result("OTP Validation", True, "Invalid OTP correctly rejected")
        else:
            results.add_result("OTP Validation", False, "Invalid OTP was accepted")
    else:
        results.add_result("OTP Validation", False, f"Unexpected status: {response.status_code}")
    
    return False, None  # We can't continue without valid OTP in automated mode

def test_unauthorized_access(results):
    """Test unauthorized access protection"""
    print("Testing unauthorized access protection...")
    
    response = make_request("GET", "/user/profile")
    if not response:
        results.add_result("Auth Protection", False, "Connection failed")
        return False
    
    # Should return 422 (Unprocessable Entity) for missing JWT
    if response.status_code in [401, 422]:
        results.add_result("Auth Protection", True, "Unauthorized access blocked")
        return True
    
    results.add_result("Auth Protection", False, f"Unexpected status: {response.status_code}")
    return False

def test_get_packages(results):
    """Test getting available packages"""
    print("Testing get packages...")
    
    response = make_request("GET", "/packages/available")
    if not response:
        results.add_result("Get Packages", False, "Connection failed")
        return False, None
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success") and data.get("data", {}).get("package"):
            package = data["data"]["package"]
            results.add_result("Get Packages", True, f"Package: {package.get('name')}")
            return True, package.get("package_id")
    elif response.status_code == 404:
        results.add_result("Get Packages", True, "No packages available (expected)")
        return True, None
    
    results.add_result("Get Packages", False, f"Status: {response.status_code}")
    return False, None

def test_invalid_phone_validation(results):
    """Test phone number validation"""
    print("Testing phone validation...")
    
    invalid_phones = [
        "invalid",
        "123456789",
        "+1234567890",  # Not Kuwait
        "96555555",     # Too short
    ]
    
    validation_working = True
    for phone in invalid_phones:
        data = {
            "phone_number": phone,
            "purpose": "login"
        }
        
        response = make_request("POST", "/auth/send-otp", data, headers)
        if not response:
            results.add_result("Phone Validation", False, "Connection failed")
            return False
            
        if response.status_code == 400:
            response_data = response.json()
            if not response_data.get("success"):
                continue  # Good, validation working correctly
        
        # If we get here, validation failed for this phone
        validation_working = False
        break
    
    if validation_working:
        results.add_result("Phone Validation", True, "Invalid phones correctly rejected")
        return True
    else:
        results.add_result("Phone Validation", False, f"Invalid phone '{phone}' was accepted")
        return False

def test_api_endpoints_structure(results):
    """Test API endpoints structure and response format"""
    print("Testing API response structure...")
    
    # Test health endpoint response structure
    response = make_request("GET", "/health")
    if response and response.status_code == 200:
        data = response.json()
        if all(key in data for key in ["success", "data", "message"]):
            results.add_result("Response Structure", True, "Standard response format")
        else:
            results.add_result("Response Structure", False, "Non-standard response format")
    else:
        results.add_result("Response Structure", False, "Health endpoint failed")

def test_version_endpoint(results):
    """Test version endpoint"""
    print("Testing version endpoint...")
    
    response = make_request("GET", "/version")
    if not response:
        results.add_result("Version Endpoint", False, "Connection failed")
        return False
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success") and data.get("data", {}).get("version"):
            results.add_result("Version Endpoint", True, f"Version: {data['data']['version']}")
            return True
    
    results.add_result("Version Endpoint", False, f"Status: {response.status_code}")
    return False

def run_automated_tests():
    """Run all automated tests"""
    print("🏥 Kuwait Medical Clinic - Automated API Tests")
    print("=" * 50)
    print(f"Testing API at: {BASE_URL}")
    print(f"Test phone number: {TEST_PHONE}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = TestResults()
    
    # Core functionality tests
    test_health_check(results)
    test_version_endpoint(results)
    test_api_endpoints_structure(results)
    
    # Authentication tests
    test_send_otp(results)
    test_verify_otp_with_mock(results)
    test_unauthorized_access(results)
    
    # Validation tests
    test_invalid_phone_validation(results)
    
    # Package tests
    test_get_packages(results)
    
    # Print results
    results.print_summary()
    
    return results.failed == 0

def run_load_test():
    """Run basic load test"""
    print("\n🔄 Running basic load test...")
    
    start_time = time.time()
    successful_requests = 0
    failed_requests = 0
    
    for i in range(10):
        response = make_request("GET", "/health")
        if response and response.status_code == 200:
            successful_requests += 1
        else:
            failed_requests += 1
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"Load test results:")
    print(f"  Requests: 10")
    print(f"  Successful: {successful_requests}")
    print(f"  Failed: {failed_requests}")
    print(f"  Duration: {duration:.2f}s")
    print(f"  Avg response time: {(duration/10)*1000:.2f}ms")

if __name__ == "__main__":
    print("🤖 Automated API Testing Suite")
    print("==============================")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not responding correctly!")
            sys.exit(1)
    except:
        print("❌ Cannot connect to server!")
        print("Make sure Flask server is running: python run.py")
        sys.exit(1)
    
    print("✅ Server is running, starting tests...\n")
    
    # Run tests
    success = run_automated_tests()
    
    # Run load test
    run_load_test()
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success:
        print("🎉 All automated tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)