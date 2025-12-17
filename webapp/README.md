# Django Backend - Attendance Management System

## Overview

This is the backend API server for the Attendance Management System built with **Django** and **Django REST Framework**. It provides RESTful APIs for mobile and web clients to perform attendance tracking, course management, and user authentication.

## Tech Stack

- **Django 6.0** - Web framework
- **Django REST Framework 3.16.1** - API framework
- **MySQL** - Database
- **PyJWT & djangorestframework_simplejwt** - JWT authentication
- **django-cors-headers** - CORS support
- **mysqlclient** - MySQL adapter for Python

## Prerequisites

- Python 3.8+
- MySQL Server
- pip (Python package manager)
- Virtual Environment

## Installation & Setup

### 1. Create Virtual Environment

```bash
cd webapp
python3 -m venv venv
```

### 2. Activate Virtual Environment

**On Linux/Mac:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Configuration

Update `webapp/settings.py` with your MySQL credentials:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'attendance_db',
        'USER': 'your_mysql_user',
        'PASSWORD': 'your_mysql_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

### 7. Run Development Server

```bash
python manage.py runserver
```

The server will start at `http://localhost:8000/`

## Project Structure

```
webapp/
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
├── core/                   # Main Django app
│   ├── models.py           # Database models
│   ├── views.py            # API views
│   ├── serializers.py      # DRF serializers
│   ├── urls.py             # App URL routing
│   └── admin.py            # Admin panel configuration
├── webapp/                 # Project configuration
│   ├── settings.py         # Django settings
│   ├── urls.py             # Project URL routing
│   ├── wsgi.py             # WSGI configuration
│   └── asgi.py             # ASGI configuration
└── venv/                   # Virtual environment (not committed)
```

## API Documentation

### Base URL
```
http://localhost:8000/api/
```

### Authentication

All protected endpoints require JWT token in the header:
```
Authorization: Bearer <your_jwt_token>
```

### API Endpoints

#### 1. Authentication

**Login**
- **Endpoint:** `POST /auth/login/`
- **Body:** 
  ```json
  {
    "username": "student",
    "password": "password123"
  }
  ```
- **Response:**
  ```json
  {
    "access": "jwt_token",
    "refresh": "refresh_token"
  }
  ```

**Refresh Token**
- **Endpoint:** `POST /auth/token/refresh/`
- **Body:**
  ```json
  {
    "refresh": "refresh_token"
  }
  ```

#### 2. Courses

**List Courses**
- **Endpoint:** `GET /courses/`
- **Auth:** Required

**Create Course**
- **Endpoint:** `POST /courses/`
- **Auth:** Admin only
- **Body:**
  ```json
  {
    "name": "Data Structures",
    "code": "CS201",
    "description": "Basic data structures"
  }
  ```

**Get Course Details**
- **Endpoint:** `GET /courses/{id}/`
- **Auth:** Required

#### 3. Attendance

**Mark Attendance**
- **Endpoint:** `POST /attendance/`
- **Auth:** Required
- **Body:**
  ```json
  {
    "course_id": 1,
    "student_id": 5,
    "date": "2025-12-17",
    "status": "present"
  }
  ```

**Get Attendance Records**
- **Endpoint:** `GET /attendance/?student_id=5&course_id=1`
- **Auth:** Required

**Get Attendance Report**
- **Endpoint:** `GET /attendance/report/?student_id=5`
- **Auth:** Required

#### 4. Users

**Get User Profile**
- **Endpoint:** `GET /users/profile/`
- **Auth:** Required

**Update User Profile**
- **Endpoint:** `PUT /users/profile/`
- **Auth:** Required
- **Body:**
  ```json
  {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com"
  }
  ```

## Models

### User
- Standard Django User model with role-based access

### Course
- `name` - Course name
- `code` - Course code
- `description` - Course description
- `instructor` - Foreign key to User

### Attendance
- `student` - Foreign key to User
- `course` - Foreign key to Course
- `date` - Attendance date
- `status` - Present/Absent/Leave
- `timestamp` - When attendance was marked

## Admin Panel

Access Django admin at: `http://localhost:8000/admin/`

Use the superuser credentials created during setup.

## CORS Configuration

CORS is configured to allow requests from:
- `http://localhost:3000` (React frontend)
- `http://localhost:8100` (Flutter web)
- `http://localhost:5000` (Development)

Update `CORS_ALLOWED_ORIGINS` in `settings.py` for production.

## Environment Variables

Create a `.env` file (not committed to git):

```
SECRET_KEY=your_django_secret_key
DEBUG=True
MYSQL_DB=attendance_db
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_HOST=localhost
MYSQL_PORT=3306
```

Load using:
```python
from decouple import config
SECRET_KEY = config('SECRET_KEY')
```

## Running Tests

```bash
python manage.py test
```

## Deployment

### Production Checklist
- [ ] Set `DEBUG = False` in settings.py
- [ ] Update `ALLOWED_HOSTS`
- [ ] Use environment variables for sensitive data
- [ ] Set up proper database backups
- [ ] Enable HTTPS
- [ ] Configure static and media files
- [ ] Use a production WSGI server (Gunicorn)

### Using Gunicorn

```bash
pip install gunicorn
gunicorn webapp.wsgi:application --bind 0.0.0.0:8000
```

## Troubleshooting

### MySQL Connection Error
```bash
# Ensure MySQL is running
mysql -u root -p
```

### Migration Issues
```bash
# Reset migrations (development only)
python manage.py migrate core zero
python manage.py migrate
```

### Port Already in Use
```bash
# Use different port
python manage.py runserver 8001
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Create a Pull Request

## License

Educational project for college coursework.

## Support

For issues and questions, please contact the development team.
