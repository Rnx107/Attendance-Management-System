/// API Configuration for Attendance Management System
///
/// This file contains all API endpoint configurations and base URL settings.
/// It supports different environments: Android emulator, iOS simulator, and production.

class ApiConfig {
  // Base URL Configuration
  // For Android emulator: Use 10.0.2.2 to access host machine
  // For iOS simulator: Use localhost or 127.0.0.1
  // For real device/production: Use actual server IP or domain
  
  static const String _androidEmulatorUrl = 'http://10.0.2.2:8000';
  static const String _iosSimulatorUrl = 'http://localhost:8000';
  static const String _productionUrl = 'https://your-production-domain.com';
  
  /// Get the base URL based on the platform and environment
  static String get baseUrl {
    // You can add logic here to detect platform or environment
    // For now, we'll default to Android emulator during development
    return _androidEmulatorUrl;
  }
  
  // API Endpoints
  static const String _apiPrefix = '/api';
  
  // Authentication endpoints
  static String get firebaseLogin => '$baseUrl$_apiPrefix/auth/firebase-login/';
  static String get firebaseLogout => '$baseUrl$_apiPrefix/auth/firebase-logout/';
  static String get verifySession => '$baseUrl$_apiPrefix/auth/verify-session/';
  static String get refreshToken => '$baseUrl$_apiPrefix/auth/refresh-token/';
  
  // User endpoints
  static String get users => '$baseUrl$_apiPrefix/users/';
  static String user(String id) => '$baseUrl$_apiPrefix/users/$id/';
  
  // Course endpoints
  static String get courses => '$baseUrl$_apiPrefix/courses/';
  static String course(String id) => '$baseUrl$_apiPrefix/courses/$id/';
  
  // Semester endpoints
  static String get semesters => '$baseUrl$_apiPrefix/semesters/';
  static String semester(String id) => '$baseUrl$_apiPrefix/semesters/$id/';
  
  // Subject endpoints
  static String get subjects => '$baseUrl$_apiPrefix/subjects/';
  static String subject(String id) => '$baseUrl$_apiPrefix/subjects/$id/';
  
  // Student endpoints
  static String get students => '$baseUrl$_apiPrefix/students/';
  static String student(String id) => '$baseUrl$_apiPrefix/students/$id/';
  
  // Teacher-Subject endpoints
  static String get teacherSubjects => '$baseUrl$_apiPrefix/teacher-subjects/';
  static String teacherSubject(String id) => '$baseUrl$_apiPrefix/teacher-subjects/$id/';
  
  // Schedule endpoints
  static String get schedules => '$baseUrl$_apiPrefix/schedules/';
  static String schedule(String id) => '$baseUrl$_apiPrefix/schedules/$id/';
  
  // Attendance endpoints
  static String get attendance => '$baseUrl$_apiPrefix/attendance/';
  static String attendanceRecord(String id) => '$baseUrl$_apiPrefix/attendance/$id/';
  
  // Timeout configurations
  static const Duration connectTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
  static const Duration sendTimeout = Duration(seconds: 30);
  
  // Headers
  static Map<String, String> get defaultHeaders => {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };
  
  /// Get headers with authorization token
  static Map<String, String> getAuthHeaders(String token) => {
    ...defaultHeaders,
    'Authorization': 'Bearer $token',
  };
}
