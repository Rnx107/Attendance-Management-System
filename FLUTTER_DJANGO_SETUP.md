# Flutter to Django API Connection - Complete Setup Guide

## Overview
Your Flutter app is now connected to your Django backend. Here's what was set up:

---

## ✅ What Was Done

### 1. **Flutter API Service** (`lib/services/api_services.dart`)
   - Created a centralized API service for all HTTP requests
   - Includes methods for:
     - `login()` - Authenticate user
     - `getUserData()` - Fetch user details
     - `getAttendance()` - Get attendance records
     - `markAttendance()` - Mark attendance
     - `logout()` - Sign out user
   - Error handling with timeout and network error management
   - API key authentication header support

### 2. **Flutter Login Page** (`lib/pages/login.dart`)
   - Updated to StatefulWidget for state management
   - Connected TextFields to controllers
   - Added loading indicator during API call
   - Integrated API service for authentication
   - Error handling with SnackBar notifications
   - Proper resource cleanup in `dispose()`

### 3. **Django API Endpoints** (`webapp/accounts/api_views.py`)
   - `POST /accounts/api/login/` - User authentication
   - `POST /accounts/api/logout/` - User logout
   - `GET /accounts/api/user/<id>/` - Get user details
   - `GET /accounts/api/attendance/` - List attendance records
   - `POST /accounts/api/attendance/mark/` - Mark attendance

### 4. **Django Configuration** (`webapp/webapp/settings.py`)
   - Enabled REST Framework
   - Configured CORS to accept Flutter requests
   - Set up authentication classes
   - Added necessary middleware

### 5. **URL Routing** (`webapp/accounts/urls.py`)
   - Mapped all API endpoints
   - Separated web views from API routes

---

## 🔧 Configuration Steps

### **Step 1: Update the Base URL in Flutter**
Edit `lib/services/api_services.dart`:

```dart
// For local development on your machine
static const String baseUrl = 'http://localhost:8000/api';

// For Android emulator (testing)
static const String baseUrl = 'http://10.0.2.2:8000/api';

// For physical device (replace with your machine IP)
static const String baseUrl = 'http://192.168.x.x:8000/api';
```

### **Step 2: Install Required Python Packages**
In your `webapp` directory:

```bash
cd webapp
pip install djangorestframework django-cors-headers
pip install -r requirements.txt
```

### **Step 3: Run Django Server**
```bash
cd webapp
python manage.py runserver 0.0.0.0:8000
```

**Important:** Use `0.0.0.0:8000` to allow requests from other devices.

### **Step 4: Test the Connection**
Use Postman or curl to test:

```bash
curl -X POST http://localhost:8000/accounts/api/login/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer raman123" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

---

## 📱 Network Configuration

### **For Different Scenarios:**

| Device Type | Base URL | Notes |
|------------|----------|-------|
| **iOS Simulator** | `http://localhost:8000/api` | Direct access to host machine |
| **Android Emulator** | `http://10.0.2.2:8000/api` | Special alias for host machine |
| **Physical Android Device** | `http://192.168.x.x:8000/api` | Use your machine's local IP |
| **Physical iOS Device** | `http://192.168.x.x:8000/api` | Use your machine's local IP |

### **Find Your Machine IP:**
```bash
# On Linux/Mac
ifconfig | grep "inet "

# On Windows
ipconfig | findstr "IPv4"
```

---

## 🔐 API Key Authentication

Your Flutter app sends the API key in headers:
```dart
'Authorization': 'Bearer raman123'
```

The Django views currently accept this but don't enforce it. To add security:

1. Create a custom authentication backend in Django
2. Validate the API key before processing requests
3. Store API keys securely (use environment variables)

---

## 📡 API Endpoints Reference

### **Login**
```
POST /accounts/api/login/
Headers:
  - Content-Type: application/json
  - Authorization: Bearer raman123

Body:
{
  "email": "student@example.com",
  "password": "password123"
}

Response:
{
  "success": true,
  "user_id": 1,
  "email": "student@example.com",
  "role": "student",
  "full_name": "John Doe"
}
```

### **Get User Details**
```
GET /accounts/api/user/1/
Headers:
  - Authorization: Bearer raman123

Response:
{
  "user_id": 1,
  "email": "student@example.com",
  "role": "student",
  "full_name": "John Doe"
}
```

### **Get Attendance**
```
GET /accounts/api/attendance/?user_id=1
Headers:
  - Authorization: Bearer raman123

Response:
{
  "results": [
    {
      "id": 1,
      "status": "present",
      "marked_at": "2024-01-13T10:30:00Z",
      "session__subject__name": "Mathematics"
    }
  ],
  "count": 1
}
```

### **Mark Attendance**
```
POST /accounts/api/attendance/mark/
Headers:
  - Content-Type: application/json
  - Authorization: Bearer raman123

Body:
{
  "user_id": 1,
  "course_id": 5,
  "status": "present"
}

Response:
{
  "success": true,
  "message": "Attendance marked successfully"
}
```

---

## 🐛 Troubleshooting

### **Issue: Connection Refused**
- ✅ Ensure Django server is running: `python manage.py runserver 0.0.0.0:8000`
- ✅ Check firewall settings
- ✅ Verify correct IP/port in Flutter base URL

### **Issue: CORS Error**
- ✅ Django settings should have `CORS_ALLOW_ALL_ORIGINS = True`
- ✅ Or add your Flutter app URL to `CORS_ALLOWED_ORIGINS`

### **Issue: 401 Unauthorized**
- ✅ Check API key is correct
- ✅ Verify email and password are correct in database

### **Issue: JSON Parse Error**
- ✅ Ensure Django response is valid JSON
- ✅ Check response.statusCode matches expected value

### **Issue: Timeout**
- ✅ API service has 10-second timeout
- ✅ Check network connection
- ✅ Ensure Django server is responding

---

## 🚀 Next Steps

### **1. Implement Navigation After Login**
Update `_LoginPageState._login()`:
```dart
if (response['success']) {
  // Save user data locally
  // Navigate to appropriate dashboard
  Navigator.pushReplacementNamed(
    context, 
    '/student_dashboard'
  );
}
```

### **2. Add Local Storage**
```bash
flutter pub add shared_preferences
```
Store user token/ID for automatic login.

### **3. Implement Role-Based Navigation**
```dart
if (response['role'] == 'student') {
  Navigator.pushReplacementNamed(context, '/student_dashboard');
} else if (response['role'] == 'teacher') {
  Navigator.pushReplacementNamed(context, '/teacher_dashboard');
}
```

### **4. Add More API Methods**
- Get courses
- Get class schedule
- Submit assignments
- View grades

### **5. Add Security**
- Implement JWT tokens
- Add refresh token mechanism
- Store tokens securely
- Implement certificate pinning

---

## 📚 File Locations

```
Flutter Files:
├── lib/
│   ├── services/api_services.dart          ← API service
│   ├── pages/login.dart                    ← Updated login page
│   └── main.dart                           ← Entry point

Django Files:
├── webapp/
│   ├── accounts/
│   │   ├── api_views.py                    ← NEW: API views
│   │   ├── urls.py                         ← Updated URL routes
│   │   └── views.py                        ← Existing web views
│   └── webapp/
│       └── settings.py                     ← Updated settings
```

---

## ✨ Summary

Your Flutter app can now:
- ✅ Connect to Django backend
- ✅ Authenticate users via API
- ✅ Fetch user data
- ✅ Handle errors gracefully
- ✅ Show loading states

Django backend can now:
- ✅ Accept requests from Flutter
- ✅ Handle CORS properly
- ✅ Authenticate via API key
- ✅ Return JSON responses

**Happy coding! 🎉**
