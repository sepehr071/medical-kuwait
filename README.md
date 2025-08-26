# Kuwait Medical Clinic Flask Backend

A comprehensive Flask REST API backend for a medical clinic system with OTP-based authentication, package subscriptions, and MongoDB integration.

## 🏗️ Architecture Overview

This Flask backend implements:
- **OTP-based Authentication** with Kuwait phone number validation
- **JWT Token Management** for secure API access
- **Package Subscription System** for medical services
- **MongoDB Integration** for data persistence
- **RESTful API Design** with standardized responses
- **Modular Architecture** with service layers and blueprints

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **MongoDB Community Server** (running locally)
- **Git** (for cloning)

### Automated Setup

Run the setup script for automatic environment configuration:

```bash
python setup_dev.py
```

This will:
- Check prerequisites
- Create virtual environment
- Install dependencies
- Set up environment files
- Initialize database with sample data

### Manual Setup

1. **Clone and navigate to the project:**
   ```bash
   cd kuwait-medical/backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/macOS
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database:**
   ```bash
   python migrations/init_db.py init
   ```

6. **Start the server:**
   ```bash
   python run.py
   ```

## 📋 API Endpoints

### Authentication

#### Send OTP
```http
POST /api/auth/send-otp
Content-Type: application/json

{
  "phone_number": "+965XXXXXXXX",
  "purpose": "login"
}
```

#### Verify OTP & Login
```http
POST /api/auth/verify-otp
Content-Type: application/json

{
  "phone_number": "+965XXXXXXXX",
  "code": "12345"
}
```

### User Management

#### Get Profile
```http
GET /api/user/profile
Authorization: Bearer <jwt_token>
```

#### Update Profile
```http
PUT /api/user/profile
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "name": "Ahmed Al-Kuwait",
  "national_id": "123456789"
}
```

#### Change Phone Number
```http
# 1. Send OTP for new phone
POST /api/user/send-phone-change-otp
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "new_phone_number": "+965XXXXXXXX"
}

# 2. Verify OTP and update phone
PUT /api/user/phone
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "new_phone_number": "+965XXXXXXXX",
  "otp_code": "12345"
}
```

### Package Management

#### Get Available Packages
```http
GET /api/packages/available
```

#### Purchase Package
```http
POST /api/packages/purchase
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "package_id": "package-uuid",
  "user_info": {
    "name": "Ahmed Al-Kuwait",
    "national_id": "123456789"
  }
}
```

#### Get Package History
```http
GET /api/packages/history
Authorization: Bearer <jwt_token>
```

### System

#### Health Check
```http
GET /api/health
```

## 📊 Response Format

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": { ... }
  }
}
```

## 🗄️ Database Schema

### Collections

- **users** - User profiles and active packages
- **packages** - Available service packages
- **otp_codes** - OTP verification codes (with TTL)
- **package_history** - Package purchase history

### Key Features

- **Embedded Documents** - Active package in user document
- **TTL Indexes** - Automatic OTP cleanup
- **Unique Constraints** - Phone numbers and IDs
- **Compound Indexes** - Optimized queries

## 🔧 Development

### Project Structure
```
backend/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models/              # Database models
│   ├── api/                 # API endpoints
│   ├── services/            # Business logic
│   ├── utils/               # Utilities and helpers
│   └── config/              # Configuration
├── migrations/              # Database scripts
├── requirements.txt         # Dependencies
├── run.py                   # Application entry point
└── setup_dev.py            # Development setup script
```

### Database Management

```bash
# Initialize database
python migrations/init_db.py init

# Check database status
python migrations/init_db.py status

# Reset database (⚠️ deletes all data)
python migrations/init_db.py reset
```

### Environment Variables

Key environment variables in `.env`:

```bash
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=kuwait_medical_clinic

# Frontend Integration
FRONTEND_URL=http://localhost:3000

# SMS Service (Placeholder)
SMS_PROVIDER=placeholder
SMS_API_KEY=placeholder_key
```

## 🔒 Security Features

- **Hashed OTP Storage** - Codes never stored in plain text
- **JWT Token Authentication** - 24-hour token expiry
- **Kuwait Phone Validation** - Specific format validation
- **Input Sanitization** - Comprehensive validation
- **CORS Configuration** - Frontend integration

## 📱 SMS Integration

The system includes a placeholder SMS service that logs OTP codes to the console for development. To integrate with a real SMS provider:

1. **Update SMS service** in `app/services/sms_service.py`
2. **Add provider credentials** to environment variables
3. **Configure provider-specific settings**

Supported providers (ready for integration):
- Twilio
- AWS SNS
- Custom REST APIs

## 🧪 Testing

The project includes a testing framework setup:

```bash
# Run tests (when test files are created)
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

## 🚀 Production Deployment

For production deployment:

1. **Environment Configuration:**
   - Set `FLASK_ENV=production`
   - Use strong secret keys
   - Configure production MongoDB URI

2. **Security Enhancements:**
   - Enable HTTPS
   - Configure proper CORS origins
   - Set up monitoring and logging

3. **Database:**
   - Use MongoDB Atlas or dedicated MongoDB instance
   - Enable authentication and SSL
   - Set up backups

4. **Server:**
   - Use Gunicorn or uWSGI
   - Configure reverse proxy (Nginx)
   - Set up SSL certificates

## 📞 Kuwait Phone Number Format

The system validates Kuwait phone numbers in these formats:
- `+965XXXXXXXX` (international format)
- `965XXXXXXXX` (country code without +)
- `8-digit local` (starting with 5, 6, or 9)

All numbers are normalized to `+965XXXXXXXX` format internally.

## 🔧 Troubleshooting

### Common Issues

1. **MongoDB Connection Failed:**
   - Ensure MongoDB is running: `mongosh`
   - Check connection string in `.env`

2. **Import Errors:**
   - Activate virtual environment
   - Install dependencies: `pip install -r requirements.txt`

3. **OTP Not Received:**
   - Check console logs for placeholder SMS output
   - Verify phone number format

4. **JWT Token Issues:**
   - Check token expiry (24 hours)
   - Verify JWT_SECRET_KEY in environment

### Database Issues

```bash
# Check database status
python migrations/init_db.py status

# Recreate indexes
python migrations/init_db.py init

# Check MongoDB logs
mongosh --eval "db.runCommand({getLog: 'global'})"
```

## 🤝 Contributing

1. Follow the existing code structure
2. Add proper error handling
3. Include docstrings for new functions
4. Update tests for new features
5. Follow PEP 8 style guidelines

## 📄 License

This project is developed for Kuwait Medical Clinic system.

---

**🏥 Kuwait Medical Clinic Flask Backend v1.0.0**  
Built with Flask, MongoDB, and JWT authentication.