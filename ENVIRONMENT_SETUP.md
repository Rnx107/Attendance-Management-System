# Environment & Test Data Setup

## 🔧 Environment Configuration

### For Development Testing

Create a `.env` file in `webapp/` directory:
```env
DEBUG=True
ALLOWED_HOSTS=*
SECRET_KEY=django-insecure-your-secret-key-here
DATABASE_URL=mysql://myuser:mypassword@127.0.0.1:3306/mydb
API_KEY=raman123
CORS_ALLOWED_ORIGINS=http://localhost:8000,http://10.0.2.2:8000,http://192.168.1.100:8000
```

### Update Django Settings to Use Environment Variables

Edit `webapp/webapp/settings.py`:
```python
import os
from pathlib import Path
from decouple import config  # pip install python-decouple

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-...')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*').split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DATABASE_NAME', default='mydb'),
        'USER': config('DATABASE_USER', default='myuser'),
        'PASSWORD': config('DATABASE_PASSWORD', default='mypassword'),
        'HOST': config('DATABASE_HOST', default='127.0.0.1'),
        'PORT': config('DATABASE_PORT', default='3306'),
    }
}
```

---

## 👥 Test User Accounts

### Create Test Users via Django Shell

```bash
cd webapp
python manage.py shell

# Execute these commands:
from core.models import User

# Create a student account
User.objects.create_user(
    email='student@example.com',
    password='password123',
    firstname='John',
    lastname='Doe',
    role='student'
)

# Create a teacher account
User.objects.create_user(
    email='teacher@example.com',
    password='password123',
    firstname='Jane',
    lastname='Smith',
    role='teacher'
)

# Create an admin account
User.objects.create_user(
    email='admin@example.com',
    password='password123',
    firstname='Admin',
    lastname='User',
    role='admin'
)

exit()
```

### Test Credentials
```
Student:
  Email: student@example.com
  Password: password123
  Role: student

Teacher:
  Email: teacher@example.com
  Password: password123
  Role: teacher

Admin:
  Email: admin@example.com
  Password: password123
  Role: admin
```

---

## 🔌 Database Connection

### MySQL Setup
```bash
# Login to MySQL
mysql -u root -p

# Create database
CREATE DATABASE mydb;

# Create user
CREATE USER 'myuser'@'localhost' IDENTIFIED BY 'mypassword';

# Grant privileges
GRANT ALL PRIVILEGES ON mydb.* TO 'myuser'@'localhost';
FLUSH PRIVILEGES;

# Verify
SHOW GRANTS FOR 'myuser'@'localhost';
exit;
```

### Django Database Migration
```bash
cd webapp
python manage.py migrate
python manage.py createsuperuser  # Create admin user
```

---

## 📱 Flutter App Environment

### Update API Service for Different Environments

Edit `lib/services/api_services.dart`:

```dart
class ApiService {
  // Environment configuration
  static const String environment = 'development'; // development, staging, production
  
  static String get baseUrl {
    switch (environment) {
      case 'production':
        return 'https://api.yourdomain.com/api';
      case 'staging':
        return 'https://staging-api.yourdomain.com/api';
      case 'development':
      default:
        return 'http://localhost:8000/api';
    }
  }

  static const String apiKey = 'raman123';
  // ... rest of code
}
```

Or use environment variables:
```bash
flutter run --dart-define=API_BASE_URL=http://localhost:8000/api
```

---

## 🧪 Testing with Postman

### Import Postman Collection

Create `postman_collection.json`:
```json
{
  "info": {
    "name": "Attendance Management API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Login",
      "request": {
        "method": "POST",
        "url": {
          "raw": "http://localhost:8000/accounts/api/login/",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["accounts", "api", "login", ""]
        },
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          },
          {
            "key": "Authorization",
            "value": "Bearer raman123"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"email\": \"student@example.com\",\n  \"password\": \"password123\"\n}"
        }
      }
    },
    {
      "name": "Get User Details",
      "request": {
        "method": "GET",
        "url": {
          "raw": "http://localhost:8000/accounts/api/user/1/",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["accounts", "api", "user", "1", ""]
        },
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer raman123"
          }
        ]
      }
    }
  ]
}
```

---

## 🐳 Docker Setup (Optional)

### docker-compose.yml for Full Stack
```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: mydb
      MYSQL_USER: myuser
      MYSQL_PASSWORD: mypassword
      MYSQL_ROOT_PASSWORD: rootpassword
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  django:
    build: ./webapp
    command: python manage.py runserver 0.0.0.0:8000
    ports:
      - "8000:8000"
    depends_on:
      - mysql
    environment:
      - DATABASE_URL=mysql://myuser:mypassword@mysql:3306/mydb
      - DEBUG=True
    volumes:
      - ./webapp:/app

volumes:
  mysql_data:
```

Run with:
```bash
docker-compose up -d
```

---

## ✅ Verification Checklist

- [ ] MySQL running and connected
- [ ] Test users created in database
- [ ] Django migrations complete
- [ ] Django server running on 0.0.0.0:8000
- [ ] API endpoints responding (test with curl/Postman)
- [ ] Flutter base URL updated
- [ ] Flutter app builds successfully
- [ ] Login request returns success for valid credentials
- [ ] Login request returns error for invalid credentials

---

## 🔍 Testing Endpoints with curl

### Test 1: Login
```bash
curl -X POST http://localhost:8000/accounts/api/login/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer raman123" \
  -d '{
    "email": "student@example.com",
    "password": "password123"
  }'
```

### Test 2: Get User
```bash
curl -X GET http://localhost:8000/accounts/api/user/1/ \
  -H "Authorization: Bearer raman123"
```

### Test 3: Get Attendance
```bash
curl -X GET "http://localhost:8000/accounts/api/attendance/?user_id=1" \
  -H "Authorization: Bearer raman123"
```

### Test 4: Mark Attendance
```bash
curl -X POST http://localhost:8000/accounts/api/attendance/mark/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer raman123" \
  -d '{
    "user_id": 1,
    "course_id": 5,
    "status": "present"
  }'
```

---

## 📝 Logging & Debugging

### Django Debug Mode
In `webapp/webapp/settings.py`:
```python
DEBUG = True  # Shows detailed error pages
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

### Flutter Debug Mode
```dart
// In lib/services/api_services.dart, add logging:
import 'package:logger/logger.dart';

final logger = Logger();

static Future<Map<String, dynamic>> login({...}) async {
  logger.d('Login request: $email');
  final response = await http.post(...);
  logger.d('Login response: ${response.body}');
  // ...
}
```

---

## 🚨 Common Setup Issues

| Issue | Solution |
|-------|----------|
| **MySQL connection refused** | Ensure MySQL is running: `mysql -u root -p` |
| **Database doesn't exist** | Create it: `CREATE DATABASE mydb;` |
| **User doesn't exist** | Create user: `CREATE USER 'myuser'@'localhost'...` |
| **Django migrations failed** | Run: `python manage.py migrate --run-syncdb` |
| **Port 8000 in use** | Use different port: `python manage.py runserver 8001` |
| **API returns 404** | Verify URL routes in accounts/urls.py |

---

**Everything is ready! Start testing! 🚀**
