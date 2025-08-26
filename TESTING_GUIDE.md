# API Testing Guide

This guide explains how to test the Kuwait Medical Clinic Flask Backend API using the provided test scripts.

## 🧪 Test Scripts Overview

### 1. Interactive Test Script (`test_api.py`)
- **Purpose**: Manual testing with real OTP input
- **Best for**: Complete end-to-end testing, manual verification
- **Requires**: Manual OTP input from server console

### 2. Automated Test Script (`test_api_automated.py`)  
- **Purpose**: Automated testing without manual input
- **Best for**: CI/CD, quick validation, load testing
- **Requires**: No manual input needed

## 🚀 Running the Tests

### Prerequisites
1. **Start the Flask server:**
   ```bash
   python run.py
   ```

2. **Initialize the database:**
   ```bash
   python migrations/init_db.py init
   ```

3. **Install requests library** (if not already installed):
   ```bash
   pip install requests
   ```

### Interactive Testing

Run the interactive test script:
```bash
python test_api.py
```

**What it tests:**
1. ✅ Health Check
2. ✅ Send OTP to phone number  
3. ✅ Verify OTP and login (requires manual input)
4. ✅ Get user profile
5. ✅ Update user profile
6. ✅ Get available packages
7. ✅ Purchase package
8. ✅ Get package history
9. ✅ Error scenarios validation

**Manual Steps:**
- When prompted, check the server console for the OTP code
- Enter the 5-digit OTP code when requested
- The script will guide you through each step

### Automated Testing

Run the automated test script:
```bash
python test_api_automated.py
```

**What it tests:**
1. ✅ Health Check
2. ✅ Version endpoint
3. ✅ API response structure
4. ✅ Send OTP functionality
5. ✅ OTP validation (with invalid codes)
6. ✅ Authorization protection
7. ✅ Phone number validation
8. ✅ Package availability
9. ✅ Basic load testing (10 requests)

## 📋 Test Scenarios

### Authentication Flow
```
1. Send OTP → POST /api/auth/send-otp
2. Check server console for OTP code
3. Verify OTP → POST /api/auth/verify-otp  
4. Receive JWT token for subsequent requests
```

### User Management Flow
```
1. Get profile → GET /api/user/profile (with JWT)
2. Update profile → PUT /api/user/profile (with JWT)
3. Change phone → POST /api/user/send-phone-change-otp + PUT /api/user/phone
```

### Package Flow
```
1. Get packages → GET /api/packages/available
2. Purchase package → POST /api/packages/purchase (with JWT)
3. Check history → GET /api/packages/history (with JWT)
```

## 🔍 Understanding Test Results

### Success Indicators
- ✅ Green checkmarks for passed tests
- 📊 Response data displayed for verification
- 🎉 "All tests passed" message at the end

### Failure Indicators  
- ❌ Red X marks for failed tests
- 📄 Error messages and status codes
- 📋 Summary of failed tests

### Warning Indicators
- ⚠️ Yellow warnings for skipped or conditional tests
- ℹ️ Informational messages for test context

## 🧪 Custom Testing

### Testing Specific Endpoints

You can modify the test scripts or use curl/Postman:

```bash
# Health check
curl -X GET http://localhost:5000/api/health

# Send OTP
curl -X POST http://localhost:5000/api/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+96551234567", "purpose": "login"}'

# Verify OTP  
curl -X POST http://localhost:5000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+96551234567", "code": "12345"}'

# Get profile (replace TOKEN with actual JWT)
curl -X GET http://localhost:5000/api/user/profile \
  -H "Authorization: Bearer TOKEN"
```

### Testing Different Phone Numbers

Update the `TEST_PHONE` variable in the test scripts:

```python
TEST_PHONE = "+96550000000"  # Your test number
```

Supported formats:
- `+965XXXXXXXX` (international)
- `965XXXXXXXX` (with country code)
- `XXXXXXXX` (8-digit local, must start with 5, 6, or 9)

## 🔧 Troubleshooting

### Common Issues

1. **Connection Errors**
   ```
   Error: Connection failed!
   Solution: Make sure Flask server is running (python run.py)
   ```

2. **Database Errors**
   ```
   Error: Database connection failed
   Solution: Ensure MongoDB is running and database is initialized
   ```

3. **OTP Not Found**
   ```
   Error: Check server console for OTP
   Solution: Look at the Flask server terminal output for the OTP code
   ```

4. **JWT Token Expired**
   ```
   Error: 401 Unauthorized  
   Solution: JWT tokens expire after 24 hours, run login test again
   ```

### Environment Issues

1. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **MongoDB Not Running**
   ```bash
   # Check if MongoDB is running
   mongosh --eval "db.runCommand('ping')"
   ```

3. **Port Conflicts**
   ```bash
   # Check if port 5000 is in use
   netstat -an | findstr :5000  # Windows
   lsof -i :5000                # macOS/Linux
   ```

## 📊 Performance Testing

The automated test includes basic load testing. For more comprehensive testing:

### Custom Load Test
```python
import time
import threading
import requests

def load_test(num_requests=100, concurrent=10):
    url = "http://localhost:5000/api/health"
    results = []
    
    def make_request():
        start = time.time()
        response = requests.get(url)
        duration = time.time() - start
        results.append((response.status_code, duration))
    
    # Create threads
    threads = []
    for i in range(concurrent):
        for j in range(num_requests // concurrent):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
    
    # Wait for completion
    for thread in threads:
        thread.join()
    
    # Analyze results
    success_count = sum(1 for status, _ in results if status == 200)
    avg_time = sum(duration for _, duration in results) / len(results)
    
    print(f"Load Test Results:")
    print(f"  Total Requests: {len(results)}")
    print(f"  Successful: {success_count}")
    print(f"  Success Rate: {success_count/len(results)*100:.1f}%")
    print(f"  Average Response Time: {avg_time*1000:.2f}ms")

# Run load test
load_test(100, 10)
```

## 📝 Test Data

### Sample Phone Numbers (Kuwait Format)
- `+96551234567` (mobile)
- `+96560000000` (mobile) 
- `+96590000000` (mobile)

### Sample User Data
```json
{
  "name": "Ahmed Al-Kuwait",
  "national_id": "123456789"
}
```

### Sample Package Data
The database initialization creates sample packages:
- **Basic Medical Package**: $50, 30 days
- **Premium Medical Package**: $100, 90 days (inactive by default)

## 🎯 Best Practices

1. **Test Environment Setup**
   - Use dedicated test database
   - Use test phone numbers
   - Don't test with production data

2. **Continuous Testing**
   - Run automated tests before commits
   - Include tests in CI/CD pipeline
   - Monitor test results regularly

3. **Manual Testing**
   - Test complete user flows manually
   - Verify OTP delivery in real environments
   - Test error scenarios thoroughly

4. **Performance Testing**
   - Test with realistic load
   - Monitor response times
   - Check database performance

---

**Happy Testing! 🧪**

For issues or questions, check the main README.md or server logs.