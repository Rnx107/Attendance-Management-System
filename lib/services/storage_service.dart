/// Storage Service for Secure Token Management
///
/// This service handles secure storage of sensitive data (tokens, Firebase UID)
/// using platform-specific encrypted storage, and non-sensitive data using
/// SharedPreferences.

import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';

class StorageService {
  // Singleton pattern
  static final StorageService _instance = StorageService._internal();
  factory StorageService() => _instance;
  StorageService._internal();
  
  // Flutter Secure Storage for sensitive data
  // Uses Keychain on iOS and EncryptedSharedPreferences on Android
  final _secureStorage = const FlutterSecureStorage(
    aOptions: AndroidOptions(
      encryptedSharedPreferences: true,
    ),
    iOptions: IOSOptions(
      accessibility: KeychainAccessibility.first_unlock_this_device,
    ),
  );
  
  // Keys for secure storage (sensitive data)
  static const String _sessionTokenKey = 'session_token';
  static const String _firebaseUidKey = 'firebase_uid';
  
  // Keys for shared preferences (non-sensitive data)
  static const String _emailKey = 'user_email';
  static const String _firstnameKey = 'user_firstname';
  static const String _lastnameKey = 'user_lastname';
  static const String _roleKey = 'user_role';
  static const String _tokenExpiryKey = 'token_expiry';
  
  // ==================== Session Token Management ====================
  
  /// Save session token securely
  Future<void> saveSessionToken(String token) async {
    try {
      await _secureStorage.write(key: _sessionTokenKey, value: token);
    } catch (e) {
      throw Exception('Failed to save session token: $e');
    }
  }
  
  /// Get session token
  Future<String?> getSessionToken() async {
    try {
      return await _secureStorage.read(key: _sessionTokenKey);
    } catch (e) {
      throw Exception('Failed to get session token: $e');
    }
  }
  
  /// Delete session token
  Future<void> deleteSessionToken() async {
    try {
      await _secureStorage.delete(key: _sessionTokenKey);
    } catch (e) {
      throw Exception('Failed to delete session token: $e');
    }
  }
  
  // ==================== Firebase UID Management ====================
  
  /// Save Firebase UID securely
  Future<void> saveFirebaseUid(String uid) async {
    try {
      await _secureStorage.write(key: _firebaseUidKey, value: uid);
    } catch (e) {
      throw Exception('Failed to save Firebase UID: $e');
    }
  }
  
  /// Get Firebase UID
  Future<String?> getFirebaseUid() async {
    try {
      return await _secureStorage.read(key: _firebaseUidKey);
    } catch (e) {
      throw Exception('Failed to get Firebase UID: $e');
    }
  }
  
  /// Delete Firebase UID
  Future<void> deleteFirebaseUid() async {
    try {
      await _secureStorage.delete(key: _firebaseUidKey);
    } catch (e) {
      throw Exception('Failed to delete Firebase UID: $e');
    }
  }
  
  // ==================== User Data Management ====================
  
  /// Save user data (non-sensitive)
  Future<void> saveUserData({
    required String email,
    required String firstname,
    required String lastname,
    required String role,
  }) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_emailKey, email);
      await prefs.setString(_firstnameKey, firstname);
      await prefs.setString(_lastnameKey, lastname);
      await prefs.setString(_roleKey, role);
    } catch (e) {
      throw Exception('Failed to save user data: $e');
    }
  }
  
  /// Get user email
  Future<String?> getUserEmail() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getString(_emailKey);
    } catch (e) {
      throw Exception('Failed to get user email: $e');
    }
  }
  
  /// Get user firstname
  Future<String?> getUserFirstname() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getString(_firstnameKey);
    } catch (e) {
      throw Exception('Failed to get user firstname: $e');
    }
  }
  
  /// Get user lastname
  Future<String?> getUserLastname() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getString(_lastnameKey);
    } catch (e) {
      throw Exception('Failed to get user lastname: $e');
    }
  }
  
  /// Get user role
  Future<String?> getUserRole() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getString(_roleKey);
    } catch (e) {
      throw Exception('Failed to get user role: $e');
    }
  }
  
  // ==================== Token Expiry Management ====================
  
  /// Save token expiry timestamp
  Future<void> saveTokenExpiry(DateTime expiry) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_tokenExpiryKey, expiry.toIso8601String());
    } catch (e) {
      throw Exception('Failed to save token expiry: $e');
    }
  }
  
  /// Get token expiry timestamp
  Future<DateTime?> getTokenExpiry() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final expiryString = prefs.getString(_tokenExpiryKey);
      if (expiryString != null) {
        return DateTime.parse(expiryString);
      }
      return null;
    } catch (e) {
      throw Exception('Failed to get token expiry: $e');
    }
  }
  
  /// Check if token is expired
  Future<bool> isTokenExpired() async {
    try {
      final expiry = await getTokenExpiry();
      if (expiry == null) return true;
      return DateTime.now().isAfter(expiry);
    } catch (e) {
      return true; // Assume expired on error
    }
  }
  
  // ==================== Clear All Data ====================
  
  /// Clear all stored data (logout)
  Future<void> clearAll() async {
    try {
      // Clear secure storage
      await _secureStorage.deleteAll();
      
      // Clear shared preferences
      final prefs = await SharedPreferences.getInstance();
      await prefs.clear();
    } catch (e) {
      throw Exception('Failed to clear all data: $e');
    }
  }
  
  // ==================== Check Authentication State ====================
  
  /// Check if user has valid session
  Future<bool> hasValidSession() async {
    try {
      final token = await getSessionToken();
      if (token == null) return false;
      
      final isExpired = await isTokenExpired();
      return !isExpired;
    } catch (e) {
      return false;
    }
  }
}
