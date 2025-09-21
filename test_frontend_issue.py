#!/usr/bin/env python3
"""
Test script to debug the frontend JSON issue
"""

import requests
import json

def test_endpoints():
    """Test all endpoints that might be causing the issue"""
    
    base_url = "http://localhost:5000/api"
    
    print("🔍 Testing Backend Endpoints for JSON Response Issues")
    print("=" * 60)
    
    # Test 1: Health endpoint
    print("\n1. Testing Health Endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Not set')}")
        if response.text:
            print(f"   Response: {response.text[:200]}...")
        else:
            print("   Response: EMPTY!")
    except Exception as e:
        print(f"   ERROR: {str(e)}")
    
    # Test 2: Debug endpoint
    print("\n2. Testing Debug Endpoint...")
    try:
        response = requests.get(f"{base_url}/auth/debug")
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Not set')}")
        if response.text:
            try:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)}")
            except:
                print(f"   Response (raw): {response.text[:200]}...")
        else:
            print("   Response: EMPTY!")
    except Exception as e:
        print(f"   ERROR: {str(e)}")
    
    # Test 3: Send OTP with Kuwait number
    print("\n3. Testing Send OTP (Kuwait number)...")
    try:
        data = {
            "phone_number": "+96550123456",
            "purpose": "login"
        }
        response = requests.post(f"{base_url}/auth/send-otp", json=data)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Not set')}")
        if response.text:
            try:
                result = response.json()
                print(f"   Response: {json.dumps(result, indent=2)}")
            except:
                print(f"   Response (raw): {response.text[:200]}...")
        else:
            print("   Response: EMPTY! ❌ This is the problem!")
    except Exception as e:
        print(f"   ERROR: {str(e)}")
    
    # Test 4: Send OTP with German number
    print("\n4. Testing Send OTP (German number)...")
    try:
        data = {
            "phone_number": "+4915157347404",
            "purpose": "login"
        }
        response = requests.post(f"{base_url}/auth/send-otp", json=data)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Not set')}")
        if response.text:
            try:
                result = response.json()
                print(f"   Response: {json.dumps(result, indent=2)}")
            except:
                print(f"   Response (raw): {response.text[:200]}...")
        else:
            print("   Response: EMPTY! ❌ This is the problem!")
    except Exception as e:
        print(f"   ERROR: {str(e)}")
    
    # Test 5: Invalid request
    print("\n5. Testing Invalid Request...")
    try:
        data = {
            "invalid_field": "test"
        }
        response = requests.post(f"{base_url}/auth/send-otp", json=data)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Not set')}")
        if response.text:
            try:
                result = response.json()
                print(f"   Response: {json.dumps(result, indent=2)}")
            except:
                print(f"   Response (raw): {response.text[:200]}...")
        else:
            print("   Response: EMPTY! ❌ This is the problem!")
    except Exception as e:
        print(f"   ERROR: {str(e)}")

    print("\n" + "=" * 60)
    print("🔍 Debugging Complete!")
    print("\nIf any endpoint shows 'EMPTY!' response, that's the cause of the frontend error.")
    print("Check the Flask server logs for more details.")

if __name__ == "__main__":
    test_endpoints()