# Attendance Management System

## Project Overview

The **Attendance Management System** is a comprehensive mobile and web application designed to streamline and automate the process of tracking student attendance. Built with modern technologies, it provides real-time attendance tracking, reporting, and analytics for educational institutions.

This is a full-stack application featuring:
- **Mobile App**: Flutter-based cross-platform mobile application
- **Backend API**: Django REST Framework with JWT authentication
- **Database**: MySQL for data persistence
- **Authentication**: Firebase Authentication with Google Sign-In
- **Real-time Updates**: Cloud Firestore integration

## Features

✅ **Student Attendance Tracking** - Mark attendance with date and time  
✅ **Course Management** - Manage multiple courses and classes  
✅ **Real-time Synchronization** - Cloud-based data sync across devices  
✅ **Attendance Reports** - Generate detailed attendance analytics  
✅ **Multi-user Support** - Role-based access (Admin, Teacher, Student)  
✅ **Cross-platform** - Android, iOS, and web support  
✅ **Secure Authentication** - JWT token-based API security  

## Tech Stack

### Frontend
- **Flutter** - Cross-platform mobile development
- **Dart** - Programming language for Flutter

### Backend
- **Django** - Web framework
- **Django REST Framework** - RESTful API development
- **Django CORS Headers** - Cross-Origin Resource Sharing

### Database & Cloud
- **MySQL** - Relational database
- **Firebase** - Authentication and Cloud Firestore

### Authentication & Security
- **PyJWT** - JWT token handling
- **djangorestframework_simplejwt** - JWT authentication for Django
- **Google Sign-In** - OAuth 2.0 authentication

## Project Structure

```
attendance_management_system/
├── lib/                    # Flutter app source code
│   ├── main.dart
│   ├── pages/              # UI pages
│   └── firebase_options.dart
├── android/                # Android native code
├── ios/                    # iOS native code
├── web/                    # Web deployment files
├── webapp/                 # Django backend API
│   ├── manage.py
│   ├── requirements.txt
│   ├── core/               # Core Django app
│   └── webapp/             # Project settings
├── test/                   # Flutter unit tests
└── README.md
```

## Installation & Setup

### Prerequisites
- Flutter SDK (latest version)
- Python 3.8+
- MySQL Server
- Git

### Frontend Setup (Flutter)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd attendance_management_system
   ```

2. **Get Flutter dependencies**
   ```bash
   flutter pub get
   ```

3. **Run the app**
   ```bash
   # For Android
   flutter run -d android
   
   # For iOS
   flutter run -d ios
   
   # For Web
   flutter run -d web
   ```

### Backend Setup (Django)

See [webapp/README.md](webapp/README.md) for detailed backend setup instructions.

## Running the Application

### Development Mode

**Flutter App:**
```bash
flutter run
```

**Django Backend:**
```bash
cd webapp
source venv/bin/activate
python manage.py runserver
```

### Production Build

**Flutter:**
```bash
# Android APK
flutter build apk

# iOS App
flutter build ios

# Web
flutter build web
```

## API Documentation

The backend provides RESTful APIs for:
- User authentication
- Course management
- Attendance tracking
- Report generation

Refer to [webapp/README.md](webapp/README.md#api-endpoints) for detailed API documentation.

## Configuration

### Firebase Setup
1. Add your `google-services.json` to `android/app/`
2. Add your `GoogleService-Info.plist` to `ios/Runner/`

### Database Configuration
Update database credentials in `webapp/webapp/settings.py`

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -m 'Add feature'`
3. Push to branch: `git push origin feature/your-feature`
4. Create a Pull Request

## License

This project is for educational purposes.

## Support

For issues and questions, please contact the development team or create an issue in the repository.
