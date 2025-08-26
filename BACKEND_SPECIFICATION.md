# Flask Backend Specification for Medical Clinic Site

## Overview

Backend API specification for a medical clinic system supporting OTP-based authentication and package purchasing. The frontend is a Next.js application that expects specific API endpoints and data structures.

## Database Models

### User
- **Primary Key:** UUID string
- **Fields:**
  - `phone_number` (string, unique, required) - Kuwait phone numbers
  - `name` (string, optional) - User's full name
  - `national_id` (string, optional) - National identification
  - `created_at`, `updated_at` (datetime)
  - `is_active` (boolean)
- **Relationships:**
  - Has one active package subscription
  - Has many package history records
  - Has many OTP codes

### Package
- **Primary Key:** UUID string
- **Fields:**
  - `name` (string, required) - Package name
  - `price` (decimal, required) - Package price
  - `duration` (integer, required) - Duration in days
  - `description` (text, optional)
  - `is_active` (boolean) - Whether package is available for purchase
  - `created_at` (datetime)
- **Relationships:**
  - Has many user subscriptions

### UserPackage (Active Subscriptions)
- **Primary Key:** UUID string
- **Fields:**
  - `user_id` (foreign key to User)
  - `package_id` (foreign key to Package)
  - `purchased_at` (datetime)
  - `expires_at` (datetime, calculated from purchase date + duration)
  - `is_active` (boolean)
  - `payment_status` (string) - pending, completed, failed
- **Computed Fields:**
  - `remaining_days` - Days until expiration

### OTPCode
- **Primary Key:** UUID string
- **Fields:**
  - `phone_number` (string, required)
  - `code` (string, required) - 5-digit numeric code
  - `purpose` (string, required) - "login" or "phone_change"
  - `user_id` (foreign key, optional)
  - `created_at` (datetime)
  - `expires_at` (datetime) - 5 minutes from creation
  - `is_used` (boolean)
  - `attempts` (integer) - Number of verification attempts

## API Endpoints

### Authentication

#### Send OTP
- **POST** `/api/auth/send-otp`
- **Purpose:** Send OTP code to phone number for login or phone change
- **Request:** Phone number and purpose
- **Response:** Success confirmation
- **Business Rules:**
  - Rate limiting: Max 3 requests per phone per 15 minutes
  - Kuwait phone validation required
  - 5-minute OTP expiry

#### Verify OTP (Login)
- **POST** `/api/auth/verify-otp`
- **Purpose:** Verify OTP and authenticate user
- **Request:** Phone number and OTP code
- **Response:** User data with JWT token
- **Business Rules:**
  - Max 3 verification attempts per OTP
  - Create user if doesn't exist
  - Include active package in response
  - Generate session JWT token

### User Management

#### Get User Profile
- **GET** `/api/user/profile`
- **Purpose:** Retrieve current user's profile
- **Authentication:** JWT required
- **Response:** Complete user data including active package

#### Update User Profile
- **PUT** `/api/user/profile`
- **Purpose:** Update user's name and national ID
- **Authentication:** JWT required
- **Request:** Name and national ID
- **Response:** Updated user data

#### Update Phone Number
- **PUT** `/api/user/phone`
- **Purpose:** Change user's phone number with OTP verification
- **Authentication:** JWT required
- **Request:** New phone number and OTP code
- **Response:** Success confirmation
- **Business Rules:**
  - Must verify OTP sent for "phone_change" purpose
  - New phone number must be unique

### Package Management

#### Get Available Packages
- **GET** `/api/packages/available`
- **Purpose:** Get currently available package for purchase
- **Response:** Package details (assuming single package system)

#### Purchase Package
- **POST** `/api/packages/purchase`
- **Purpose:** Purchase a package for authenticated user
- **Authentication:** JWT required
- **Request:** Package ID and user information
- **Response:** Purchase confirmation with package details
- **Business Rules:**
  - Users can only have one active package
  - Update user profile with provided information
  - Calculate expiry date based on package duration

## Authentication Flow

### JWT Token Structure
- **Payload:** User ID, phone number, issued/expiry timestamps
- **Expiry:** 24 hours
- **Usage:** Required for all user-specific endpoints

### OTP Workflow
1. **Login Process:**
   - User enters phone number
   - System sends 5-digit OTP via SMS
   - User enters OTP code
   - System verifies and creates/retrieves user
   - Returns user data and JWT token

2. **Phone Change Process:**
   - User requests phone change with new number
   - System sends OTP to new phone number
   - User enters OTP code
   - System verifies and updates phone number

## Data Validation Requirements

### Phone Number Validation
- **Format:** Kuwait numbers only
- **Patterns:** `+965XXXXXXXX`, `965XXXXXXXX`, or `8-digit starting with 5/6/9`
- **Normalization:** Always store as `+965XXXXXXXX` format

### Input Limits
- **Name:** Maximum 100 characters
- **National ID:** Maximum 50 characters
- **Phone Number:** Standardized Kuwait format

## Business Rules

### Package Subscription
- Users can only have one active package at a time
- Package expiry calculated from purchase date + duration days
- Remaining time calculated dynamically

### OTP Security
- 5-minute expiry time
- Maximum 3 verification attempts
- Rate limiting per phone number and IP address
- Different purposes: "login" and "phone_change"

### User Management
- Users created automatically on first successful OTP verification
- Phone number serves as unique identifier
- Profile information (name, national ID) optional but required for package purchase

## Response Format Standards

### Success Response
```
{
  "success": true,
  "data": { /* response data */ },
  "message": "Operation completed successfully"
}
```

### Error Response
```
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": { /* field-specific errors */ }
  }
}
```

## Rate Limiting Requirements

### OTP Endpoints
- 3 requests per phone number per 15 minutes
- 10 requests per IP address per hour

### General API
- 100 requests per minute for authenticated users
- 20 requests per minute for unauthenticated requests

## Security Considerations

- Implement CORS for frontend domain
- Validate all inputs against expected formats
- Use parameterized database queries
- Hash OTP codes in database
- Implement secure JWT token generation
- Clear expired OTP codes regularly
- Log security events for monitoring

## Frontend Integration Notes

The frontend expects exact response formats as specified. Key integration points:

- User object must include `activePackage` field when package exists
- Package object requires `remainingTime` field for active packages
- Error responses must include `success: false` flag
- JWT token included in login response for subsequent requests
- Phone numbers normalized to Kuwait format in all responses

This specification provides all necessary information for implementing a Flask backend that seamlessly integrates with the existing Next.js frontend application.