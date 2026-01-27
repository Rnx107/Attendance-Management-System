import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiService {
  // Replace with your Django server IP/domain
  // For local testing: http://localhost:8000
  // For Android emulator: http://10.0.2.2:8000
  // For physical device: http://YOUR_MACHINE_IP:8000
  static const String baseUrl = 'http://localhost:8000/api';
  static const String apiKey = 'raman123';

  /// Login endpoint - authenticates user with email and password
  /// Returns user data on success
  static Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/accounts/login/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $apiKey',
        },
        body: jsonEncode({
          'email': email,
          'password': password,
        }),
      ).timeout(
        const Duration(seconds: 10),
        onTimeout: () => throw Exception('Request timeout'),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return {
          'success': true,
          ...data,
        };
      } else if (response.statusCode == 401) {
        return {
          'success': false,
          'error': 'Invalid email or password',
        };
      } else {
        return {
          'success': false,
          'error': 'Server error: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error: $e',
      };
    }
  }

  /// Get user data by user ID
  static Future<Map<String, dynamic>> getUserData(String userId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/users/$userId/'),
        headers: {
          'Authorization': 'Bearer $apiKey',
          'Content-Type': 'application/json',
        },
      ).timeout(
        const Duration(seconds: 10),
        onTimeout: () => throw Exception('Request timeout'),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to fetch user data: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error: $e');
    }
  }

  /// Get attendance records for a user
  static Future<List<dynamic>> getAttendance(String userId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/attendance/?user_id=$userId'),
        headers: {
          'Authorization': 'Bearer $apiKey',
          'Content-Type': 'application/json',
        },
      ).timeout(
        const Duration(seconds: 10),
        onTimeout: () => throw Exception('Request timeout'),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['results'] ?? [];
      } else {
        throw Exception('Failed to fetch attendance');
      }
    } catch (e) {
      throw Exception('Error: $e');
    }
  }

  /// Mark attendance
  static Future<Map<String, dynamic>> markAttendance({
    required String userId,
    required String courseId,
    required String status,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/attendance/mark/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $apiKey',
        },
        body: jsonEncode({
          'user_id': userId,
          'course_id': courseId,
          'status': status,
        }),
      ).timeout(
        const Duration(seconds: 10),
        onTimeout: () => throw Exception('Request timeout'),
      );

      if (response.statusCode == 201 || response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to mark attendance: ${response.body}');
      }
    } catch (e) {
      throw Exception('Error: $e');
    }
  }

  /// Logout user
  static Future<bool> logout(String userId) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/accounts/logout/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $apiKey',
        },
        body: jsonEncode({'user_id': userId}),
      ).timeout(
        const Duration(seconds: 10),
        onTimeout: () => throw Exception('Request timeout'),
      );

      return response.statusCode == 200;
    } catch (e) {
      throw Exception('Error: $e');
    }
  }
}