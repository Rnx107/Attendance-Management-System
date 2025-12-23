# Firebase-Django Authentication Setup Guide

This guide explains how to set up and use the secure authentication tunnel between Firebase Google Login (Flutter) and Django backend for the Attendance Management System.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Django Backend Setup](#django-backend-setup)
3. [Flutter Frontend Setup](#flutter-frontend-setup)
4. [Authentication Flow](#authentication-flow)
5. [API Endpoints](#api-endpoints)
6. [Security Features](#security-features)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Services
- Firebase project with Authentication enabled
- Google Sign-In configured in Firebase Console
- MySQL database
- Python 3.10+
- Flutter 3.10+

### Required Packages
All packages are listed in their respective dependency files:
- Django: `webapp/requirements.txt`
- Flutter: `pubspec.yaml`

## Django Backend Setup

### Step 1: Install Dependencies

```bash
cd webapp
pip install -r requirements.txt
```

### Step 2: Configure Firebase Admin SDK

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Go to Project Settings > Service Accounts
4. Click "Generate New Private Key"
5. Save the JSON file securely (DO NOT commit to git)

### Step 3: Configure Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and configure:
```env
# Django Configuration
SECRET_KEY=your-django-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=mydb
DB_USER=myuser
DB_PASSWORD=mypassword
DB_HOST=127.0.0.1
DB_PORT=3306

# Firebase Configuration
FIREBASE_CREDENTIALS_PATH=/path/to/your/firebase-service-account.json

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:8000,http://10.0.2.2:8000
CORS_ALLOW_ALL_ORIGINS=True  # Set to False in production
```

### Step 4: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Start Django Server

```bash
python manage.py runserver 0.0.0.0:8000
```

## Flutter Frontend Setup

### Step 1: Install Dependencies

```bash
flutter pub get
```

### Step 2: Configure API Base URL

Edit `lib/config/api_config.dart` to set the correct base URL for your environment:

```dart
class ApiConfig {
  // For Android emulator: Use 10.0.2.2 to access host machine
  static const String _androidEmulatorUrl = 'http://10.0.2.2:8000';
  
  // For iOS simulator: Use localhost or 127.0.0.1
  static const String _iosSimulatorUrl = 'http://localhost:8000';
  
  // For real device/production: Use actual server IP or domain
  static const String _productionUrl = 'https://your-production-domain.com';
  
  static String get baseUrl {
    // Change this based on your needs
    return _androidEmulatorUrl;
  }
}
```

### Step 3: Run Flutter App

```bash
# For Android
flutter run

# For iOS
flutter run

# For web
flutter run -d chrome
```

## Authentication Flow

### Complete Flow Diagram

```
┌─────────────┐
│   Flutter   │
│   App       │
└──────┬──────┘
       │
       │ 1. User clicks "Sign in with Google"
       ▼
┌─────────────────┐
│ Google Sign-In  │
│   & Firebase    │
└──────┬──────────┘
       │
       │ 2. Get Firebase ID Token
       ▼
┌──────────────────┐
│  Flutter App     │
│  Extract Token   │
└──────┬───────────┘
       │
       │ 3. POST to /api/auth/firebase-login/
       │    Body: { "idToken": "..." }
       ▼
┌──────────────────┐
│  Django Backend  │
│  Verify Token    │
└──────┬───────────┘
       │
       │ 4. Firebase Admin SDK verifies token
       │ 5. Get/Create User in database
       │ 6. Generate Django JWT session token
       ▼
┌──────────────────┐
│  Flutter App     │
│  Store Token     │
└──────┬───────────┘
       │
       │ 7. Token stored securely
       │    - FlutterSecureStorage: Session token, Firebase UID
       │    - SharedPreferences: User data, expiry
       ▼
┌──────────────────┐
│  Protected APIs  │
│  Use Token       │
└──────────────────┘
```

### Key Components

#### 1. Firebase Authentication (`lib/services/auth_service.dart`)
- Handles Google Sign-In via Firebase
- Extracts Firebase ID token
- Communicates with Django backend

#### 2. Django Token Verification (`webapp/core/firebase_config.py`)
- Verifies Firebase ID tokens using Firebase Admin SDK
- Fetches user details from Firebase

#### 3. Custom DRF Authentication (`webapp/core/authentication.py`)
- Extends `BaseAuthentication`
- Validates Firebase tokens on each request
- Creates/retrieves Django users

#### 4. Session Management (`lib/services/storage_service.dart`)
- Secure storage using platform-specific encryption
- Token expiry tracking
- Automatic cleanup on logout

## API Endpoints

### Authentication Endpoints

#### 1. Firebase Login
```http
POST /api/auth/firebase-login/
Content-Type: application/json

{
  "idToken": "firebase_id_token_here"
}

Response (200 OK):
{
  "success": true,
  "token": "django_session_token",
  "expires_at": "2024-01-01T12:00:00Z",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "firstname": "John",
    "lastname": "Doe",
    "role": "student"
  }
}
```

#### 2. Verify Session
```http
GET /api/auth/verify-session/
Authorization: Bearer django_session_token

Response (200 OK):
{
  "success": true,
  "valid": true,
  "user": { ... }
}
```

#### 3. Refresh Token
```http
POST /api/auth/refresh-token/
Content-Type: application/json

{
  "idToken": "new_firebase_id_token"
}

Response (200 OK):
{
  "success": true,
  "token": "new_django_session_token",
  "expires_at": "2024-01-01T13:00:00Z",
  "user": { ... }
}
```

#### 4. Logout
```http
POST /api/auth/firebase-logout/
Authorization: Bearer django_session_token

Response (200 OK):
{
  "success": true,
  "message": "Logged out successfully"
}
```

### Protected Endpoints

All other API endpoints require authentication. Include the session token in the Authorization header:

```http
GET /api/users/
Authorization: Bearer django_session_token
```

## Security Features

### 1. Token Security
- **JWT Session Tokens**: 1-hour expiration
- **Firebase ID Tokens**: Server-side verification
- **Secure Storage**: Platform-specific encryption
  - iOS: Keychain with `first_unlock_this_device`
  - Android: EncryptedSharedPreferences

### 2. Environment Variables
Sensitive data never hardcoded:
- Django SECRET_KEY
- Database credentials
- Firebase service account path
- CORS origins

### 3. CORS Configuration
Properly configured for development and production:
```python
# Development
CORS_ALLOW_ALL_ORIGINS = True

# Production
CORS_ALLOWED_ORIGINS = ['https://your-domain.com']
CORS_ALLOW_ALL_ORIGINS = False
```

### 4. Firebase Admin SDK
- Server-side token verification
- No client-side token trust
- Cryptographic signature validation

### 5. Django REST Framework
- Custom authentication backend
- Per-endpoint permission classes
- Bearer token authentication

## Troubleshooting

### Common Issues

#### 1. "Firebase credentials not found"
**Solution**: 
- Ensure `FIREBASE_CREDENTIALS_PATH` is set in `.env`
- Verify the file path is correct and accessible
- Check file permissions

#### 2. "CORS error in Flutter"
**Solution**:
- Verify `CORS_ALLOWED_ORIGINS` includes your Flutter app's origin
- For development, set `CORS_ALLOW_ALL_ORIGINS = True`
- Ensure `CorsMiddleware` is at the top of `MIDDLEWARE` list

#### 3. "Token has expired"
**Solution**:
- Tokens expire after 1 hour
- Use the refresh token endpoint
- Flutter app automatically refreshes on certain actions

#### 4. "Network error: Connection refused"
**Solution**:
- Verify Django server is running
- Check API base URL in `lib/config/api_config.dart`
- For Android emulator, use `10.0.2.2` instead of `localhost`
- For iOS simulator, use `localhost`

#### 5. "User not found in token"
**Solution**:
- Ensure Google Sign-In is properly configured in Firebase
- Verify email scope is requested
- Check Firebase Console for user data

### Debug Mode

Enable debug logging:

**Django (`webapp/webapp/settings.py`):**
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```

**Flutter:**
```dart
// In lib/services/auth_service.dart
print('Firebase ID Token: $firebaseIdToken');
print('Backend Response: $responseData');
```

### Testing Authentication Flow

1. **Test Firebase Login**:
```bash
curl -X POST http://localhost:8000/api/auth/firebase-login/ \
  -H "Content-Type: application/json" \
  -d '{"idToken": "your_firebase_token"}'
```

2. **Test Session Verification**:
```bash
curl -X GET http://localhost:8000/api/auth/verify-session/ \
  -H "Authorization: Bearer your_session_token"
```

3. **Test Protected Endpoint**:
```bash
curl -X GET http://localhost:8000/api/users/ \
  -H "Authorization: Bearer your_session_token"
```

## Production Checklist

Before deploying to production:

- [ ] Set `DEBUG = False` in Django settings
- [ ] Use strong `SECRET_KEY`
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Set `CORS_ALLOW_ALL_ORIGINS = False`
- [ ] Configure specific `CORS_ALLOWED_ORIGINS`
- [ ] Ensure Firebase credentials are securely stored
- [ ] Use HTTPS for all API communication
- [ ] Configure proper database backup
- [ ] Set up monitoring and logging
- [ ] Review all error messages (don't expose internals)
- [ ] Test token expiration and refresh flow
- [ ] Verify secure storage is working on all platforms

## Additional Resources

- [Firebase Authentication Documentation](https://firebase.google.com/docs/auth)
- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [Flutter Secure Storage](https://pub.dev/packages/flutter_secure_storage)
- [Provider State Management](https://pub.dev/packages/provider)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Django and Flutter logs
3. Verify environment configuration
4. Check Firebase Console for auth issues
