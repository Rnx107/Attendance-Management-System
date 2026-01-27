# 🚀 Quick Start Guide - Flutter to Django Connection

## 5-Minute Setup

### Step 1: Install Dependencies (1 min)
```bash
cd /path/to/webapp
pip install djangorestframework django-cors-headers
```

### Step 2: Find Your Machine IP (30 sec)
```bash
# Linux/Mac
ifconfig | grep "inet " | grep -v 127.0.0.1

# Windows
ipconfig | findstr "IPv4"
```
**Example:** `192.168.1.100`

### Step 3: Update Flutter Base URL (1 min)
Edit: `lib/services/api_services.dart`

**Line 11:**
```dart
// Choose based on your testing environment:

// Option A: Local machine (macOS/Linux dev)
static const String baseUrl = 'http://localhost:8000/api';

// Option B: Android emulator
static const String baseUrl = 'http://10.0.2.2:8000/api';

// Option C: Physical device (replace 192.168.1.100 with YOUR IP)
static const String baseUrl = 'http://192.168.1.100:8000/api';
```

### Step 4: Start Django Server (1 min)
```bash
cd /path/to/webapp
python manage.py runserver 0.0.0.0:8000
```

### Step 5: Run Flutter App (1 min)
```bash
flutter run
```

**Done! 🎉**

---

## Test It Now

1. Open Flutter app on your device
2. Enter email: `test@example.com`
3. Enter password: `password123`
4. Click "Login"
5. You should see a success message

---

## What Each File Does

| File | Purpose |
|------|---------|
| `lib/services/api_services.dart` | Handles all HTTP requests to Django |
| `lib/pages/login.dart` | Login UI with API integration |
| `webapp/accounts/api_views.py` | Django REST API endpoints |
| `webapp/accounts/urls.py` | Routes API requests to views |
| `webapp/webapp/settings.py` | Django CORS & REST config |

---

## API Endpoints Ready to Use

```
✅ POST   /accounts/api/login/           - Login user
✅ POST   /accounts/api/logout/          - Logout user
✅ GET    /accounts/api/user/<id>/       - Get user info
✅ GET    /accounts/api/attendance/      - Get attendance
✅ POST   /accounts/api/attendance/mark/ - Mark attendance
```

---

## Troubleshooting (30 seconds)

**Can't connect?**
```bash
# Test Django is running
curl http://localhost:8000/admin/

# Test API endpoint
curl -X POST http://localhost:8000/accounts/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

**Still stuck?**
- ✅ Check base URL matches your network setup
- ✅ Ensure Django runs on `0.0.0.0:8000` (not just `localhost`)
- ✅ Check firewall isn't blocking port 8000
- ✅ Verify WiFi: device and machine on same network

---

## Device-Specific Setup

### iOS Simulator
```dart
static const String baseUrl = 'http://localhost:8000/api';
```
✅ Works directly because simulator shares localhost with Mac

### Android Emulator
```dart
static const String baseUrl = 'http://10.0.2.2:8000/api';
```
✅ Use `10.0.2.2` instead of `localhost` to reach host machine

### Physical Device (Android/iOS)
```dart
static const String baseUrl = 'http://192.168.1.100:8000/api';  // Your machine IP
```
✅ Device must be on **same WiFi network** as your machine

---

## Made Changes To

✅ `lib/services/api_services.dart` - Complete API service  
✅ `lib/pages/login.dart` - Login with API integration  
✅ `webapp/accounts/api_views.py` - NEW REST API views  
✅ `webapp/accounts/urls.py` - Added API routes  
✅ `webapp/webapp/settings.py` - REST & CORS config  

---

## Next Features to Add

- [ ] Local storage (save user token)
- [ ] Auto-login on app restart
- [ ] Navigate to dashboard after login
- [ ] Show user details page
- [ ] Attendance marking feature
- [ ] Course listing
- [ ] Class schedule view

---

## Need Help?

See detailed docs:
- 📖 [FLUTTER_DJANGO_SETUP.md](./FLUTTER_DJANGO_SETUP.md) - Complete guide
- ✅ [INTEGRATION_CHECKLIST.md](./INTEGRATION_CHECKLIST.md) - Full checklist

---

**You're all set! Happy coding! 🎉**
