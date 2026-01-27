# Flutter-Django Integration Checklist

## ✅ Completed Tasks

### Flutter Setup
- [x] Added `http` package to `pubspec.yaml`
- [x] Created `lib/services/api_services.dart` with all API methods
- [x] Updated `lib/pages/login.dart` to use API service
- [x] Added error handling and loading states
- [x] Implemented email/password validation

### Django Setup
- [x] Created `webapp/accounts/api_views.py` with REST endpoints
- [x] Updated `webapp/accounts/urls.py` with API routes
- [x] Configured `webapp/webapp/settings.py`:
  - [x] Added REST Framework
  - [x] Added CORS headers
  - [x] Set ALLOWED_HOSTS
  - [x] Configured REST_FRAMEWORK settings
  - [x] Fixed CORS middleware order

### API Endpoints Available
- [x] `POST /accounts/api/login/` - User authentication
- [x] `POST /accounts/api/logout/` - Logout
- [x] `GET /accounts/api/user/<id>/` - User details
- [x] `GET /accounts/api/attendance/` - Attendance list
- [x] `POST /accounts/api/attendance/mark/` - Mark attendance

---

## 📋 Before Running (DO THESE STEPS)

### Step 1: Install Python Packages
```bash
cd webapp
pip install djangorestframework django-cors-headers
pip install -r requirements.txt
```

### Step 2: Update Flutter Base URL
**File:** `lib/services/api_services.dart`

**Change this line based on your device:**
```dart
// For local testing on your computer
static const String baseUrl = 'http://localhost:8000/api';

// For Android emulator
static const String baseUrl = 'http://10.0.2.2:8000/api';

// For physical device (replace 192.168.x.x with your IP)
static const String baseUrl = 'http://192.168.1.100:8000/api';
```

### Step 3: Start Django Server
```bash
cd webapp
python manage.py runserver 0.0.0.0:8000
```

### Step 4: Run Flutter App
```bash
flutter run
```

---

## 🧪 Testing the Connection

### Test 1: Check Django is Running
```bash
curl http://localhost:8000/admin/
```
Should return the admin page HTML.

### Test 2: Test Login API
```bash
curl -X POST http://localhost:8000/accounts/api/login/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer raman123" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

Should return:
```json
{
  "success": true,
  "user_id": 1,
  "email": "test@example.com",
  "role": "student",
  "full_name": "John Doe"
}
```

### Test 3: Flutter Login Screen
- Open Flutter app
- Enter valid email and password
- Click "Login"
- Should see success message or error message

---

## 🔒 Important Security Notes

⚠️ **Current Setup is for DEVELOPMENT ONLY**

For production, you MUST:
- [ ] Use HTTPS instead of HTTP
- [ ] Implement proper JWT token authentication
- [ ] Remove `CORS_ALLOW_ALL_ORIGINS = True`
- [ ] Use environment variables for secrets
- [ ] Implement token refresh mechanism
- [ ] Add input validation
- [ ] Use certificate pinning
- [ ] Implement rate limiting
- [ ] Add request logging

---

## 🔧 Configuration Details

### API Service Configuration (Flutter)
**File:** `lib/services/api_services.dart`
- Base URL: Update to match your Django server
- API Key: Currently set to 'raman123' (insecure, use env vars)
- Timeout: 10 seconds

### Django Configuration
**File:** `webapp/webapp/settings.py`
- `DEBUG = True` (only for development)
- `ALLOWED_HOSTS = ['*']` (only for development)
- `CORS_ALLOW_ALL_ORIGINS = True` (only for development)
- REST Framework authentication: Token & Session

---

## 📱 Device Network Setup

### Android Emulator
```dart
static const String baseUrl = 'http://10.0.2.2:8000/api';
```

### iOS Simulator
```dart
static const String baseUrl = 'http://localhost:8000/api';
```

### Physical Device (Android/iOS)
1. Find your machine IP:
   ```bash
   ipconfig  # Windows
   ifconfig  # Mac/Linux
   ```
2. Update Flutter:
   ```dart
   static const String baseUrl = 'http://192.168.1.100:8000/api';  // Replace with your IP
   ```
3. Ensure device is on same WiFi network

---

## 🐛 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| **Connection Refused** | Check Django is running with `python manage.py runserver 0.0.0.0:8000` |
| **CORS Error** | Ensure `CORS_ALLOW_ALL_ORIGINS = True` in Django settings.py |
| **Invalid Email/Password** | Verify user exists in database and password is correct |
| **JSON Parse Error** | Check Django returns valid JSON (use browser to test) |
| **Timeout** | Increase timeout in api_services.dart or check network |
| **404 Not Found** | Verify API endpoint path and Django URL routing |

---

## 📞 API Response Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid input data
- `401 Unauthorized` - Authentication failed (invalid credentials)
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## 🎯 Next Steps After Setup

1. **Test Login** - Verify authentication works
2. **Add Local Storage** - Store user token locally
3. **Implement Dashboard** - Show appropriate dashboard after login
4. **Add More APIs** - Implement remaining features
5. **Improve Security** - Add JWT, token refresh, etc.
6. **Handle Errors** - Add better error messages
7. **Add Loading States** - Improve UX during API calls

---

## 📚 Files Modified/Created

```
Created:
  ├── webapp/accounts/api_views.py (NEW - API endpoints)
  ├── FLUTTER_DJANGO_SETUP.md (NEW - This guide)
  └── INTEGRATION_CHECKLIST.md (NEW - This checklist)

Modified:
  ├── lib/services/api_services.dart (Complete rewrite)
  ├── lib/pages/login.dart (Added API integration)
  ├── webapp/accounts/urls.py (Added API routes)
  └── webapp/webapp/settings.py (Added REST Framework & CORS)

Unchanged (But working with new APIs):
  ├── webapp/accounts/views.py (Web views, API in separate file)
  ├── lib/main.dart
  └── pubspec.yaml (http package already added)
```

---

## ✨ Ready to Go!

Your Flutter-Django integration is complete. Follow the **Before Running** section above and you're all set! 🚀
