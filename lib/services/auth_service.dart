/// Authentication Service for Firebase-Django Integration
///
/// This service handles the complete authentication flow:
/// 1. Google Sign-In via Firebase
/// 2. Firebase ID token extraction
/// 3. Django backend authentication
/// 4. Session token management

import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:firebase_auth/firebase_auth.dart';
import 'package:google_sign_in/google_sign_in.dart';
import '../config/api_config.dart';
import 'storage_service.dart';

class AuthService {
  // Singleton pattern
  static final AuthService _instance = AuthService._internal();
  factory AuthService() => _instance;
  AuthService._internal();
  
  final FirebaseAuth _firebaseAuth = FirebaseAuth.instance;
  final GoogleSignIn _googleSignIn = GoogleSignIn();
  final StorageService _storage = StorageService();
  
  // ==================== Sign In with Google ====================
  
  /// Complete Google Sign-In flow with Firebase and Django backend
  ///
  /// Returns a map containing:
  /// - success: bool
  /// - message: String (error message if failed)
  /// - user: Map (user data if successful)
  Future<Map<String, dynamic>> signInWithGoogle() async {
    try {
      // Step 1: Sign in with Google
      final GoogleSignInAccount? googleUser = await _googleSignIn.signIn();
      
      if (googleUser == null) {
        return {
          'success': false,
          'message': 'Google sign-in was cancelled',
        };
      }
      
      // Step 2: Get Google authentication details
      final GoogleSignInAuthentication googleAuth = await googleUser.authentication;
      
      // Step 3: Create Firebase credential
      final credential = GoogleAuthProvider.credential(
        accessToken: googleAuth.accessToken,
        idToken: googleAuth.idToken,
      );
      
      // Step 4: Sign in to Firebase
      final UserCredential userCredential = 
          await _firebaseAuth.signInWithCredential(credential);
      
      // Step 5: Get Firebase ID token
      final String? firebaseIdToken = await userCredential.user?.getIdToken();
      
      if (firebaseIdToken == null) {
        return {
          'success': false,
          'message': 'Failed to get Firebase ID token',
        };
      }
      
      // Step 6: Save Firebase UID
      await _storage.saveFirebaseUid(userCredential.user!.uid);
      
      // Step 7: Authenticate with Django backend
      final backendResult = await _authenticateWithBackend(firebaseIdToken);
      
      return backendResult;
      
    } on FirebaseAuthException catch (e) {
      return {
        'success': false,
        'message': 'Firebase authentication failed: ${e.message}',
      };
    } catch (e) {
      return {
        'success': false,
        'message': 'Sign-in failed: $e',
      };
    }
  }
  
  // ==================== Authenticate with Django Backend ====================
  
  /// Send Firebase ID token to Django backend for verification and session creation
  Future<Map<String, dynamic>> _authenticateWithBackend(String firebaseIdToken) async {
    try {
      final response = await http.post(
        Uri.parse(ApiConfig.firebaseLogin),
        headers: ApiConfig.defaultHeaders,
        body: jsonEncode({
          'idToken': firebaseIdToken,
        }),
      ).timeout(ApiConfig.connectTimeout);
      
      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200 && responseData['success'] == true) {
        // Save session token
        await _storage.saveSessionToken(responseData['token']);
        
        // Save token expiry
        final expiryString = responseData['expires_at'];
        if (expiryString != null) {
          await _storage.saveTokenExpiry(DateTime.parse(expiryString));
        }
        
        // Save user data
        final userData = responseData['user'];
        await _storage.saveUserData(
          email: userData['email'],
          firstname: userData['firstname'] ?? '',
          lastname: userData['lastname'] ?? '',
          role: userData['role'] ?? 'student',
        );
        
        return {
          'success': true,
          'user': userData,
        };
      } else {
        return {
          'success': false,
          'message': responseData['error'] ?? 'Authentication failed',
        };
      }
    } on http.ClientException catch (e) {
      return {
        'success': false,
        'message': 'Network error: $e',
      };
    } catch (e) {
      return {
        'success': false,
        'message': 'Backend authentication failed: $e',
      };
    }
  }
  
  // ==================== Refresh Session Token ====================
  
  /// Refresh Django session token using a fresh Firebase ID token
  Future<Map<String, dynamic>> refreshSessionToken() async {
    try {
      // Get current Firebase user
      final user = _firebaseAuth.currentUser;
      if (user == null) {
        return {
          'success': false,
          'message': 'No authenticated user',
        };
      }
      
      // Get fresh Firebase ID token
      final String? firebaseIdToken = await user.getIdToken(true); // Force refresh
      
      if (firebaseIdToken == null) {
        return {
          'success': false,
          'message': 'Failed to get Firebase ID token',
        };
      }
      
      // Call refresh token endpoint
      final response = await http.post(
        Uri.parse(ApiConfig.refreshToken),
        headers: ApiConfig.defaultHeaders,
        body: jsonEncode({
          'idToken': firebaseIdToken,
        }),
      ).timeout(ApiConfig.connectTimeout);
      
      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200 && responseData['success'] == true) {
        // Save new session token
        await _storage.saveSessionToken(responseData['token']);
        
        // Save token expiry
        final expiryString = responseData['expires_at'];
        if (expiryString != null) {
          await _storage.saveTokenExpiry(DateTime.parse(expiryString));
        }
        
        return {
          'success': true,
          'message': 'Token refreshed successfully',
        };
      } else {
        return {
          'success': false,
          'message': responseData['error'] ?? 'Token refresh failed',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Token refresh failed: $e',
      };
    }
  }
  
  // ==================== Verify Session ====================
  
  /// Verify session validity with Django backend
  Future<Map<String, dynamic>> verifySession() async {
    try {
      final sessionToken = await _storage.getSessionToken();
      
      if (sessionToken == null) {
        return {
          'success': false,
          'message': 'No session token found',
        };
      }
      
      // Check if token is expired locally first
      final isExpired = await _storage.isTokenExpired();
      if (isExpired) {
        return {
          'success': false,
          'message': 'Session token expired',
        };
      }
      
      // Verify with backend
      final response = await http.get(
        Uri.parse(ApiConfig.verifySession),
        headers: ApiConfig.getAuthHeaders(sessionToken),
      ).timeout(ApiConfig.connectTimeout);
      
      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200 && responseData['success'] == true) {
        return {
          'success': true,
          'valid': responseData['valid'],
          'user': responseData['user'],
        };
      } else {
        return {
          'success': false,
          'message': 'Session verification failed',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Session verification failed: $e',
      };
    }
  }
  
  // ==================== Sign Out ====================
  
  /// Complete sign-out flow: Firebase, Google, and clear local data
  Future<Map<String, dynamic>> signOut() async {
    try {
      // Notify backend (optional, for logging)
      final sessionToken = await _storage.getSessionToken();
      if (sessionToken != null) {
        try {
          await http.post(
            Uri.parse(ApiConfig.firebaseLogout),
            headers: ApiConfig.getAuthHeaders(sessionToken),
          ).timeout(ApiConfig.connectTimeout);
        } catch (e) {
          // Ignore backend errors during logout
        }
      }
      
      // Sign out from Firebase
      await _firebaseAuth.signOut();
      
      // Sign out from Google
      await _googleSignIn.signOut();
      
      // Clear all local storage
      await _storage.clearAll();
      
      return {
        'success': true,
        'message': 'Signed out successfully',
      };
    } catch (e) {
      return {
        'success': false,
        'message': 'Sign-out failed: $e',
      };
    }
  }
  
  // ==================== Get Auth Headers ====================
  
  /// Get authorization headers for API calls
  Future<Map<String, String>?> getAuthHeaders() async {
    try {
      final sessionToken = await _storage.getSessionToken();
      if (sessionToken == null) return null;
      
      return ApiConfig.getAuthHeaders(sessionToken);
    } catch (e) {
      return null;
    }
  }
  
  // ==================== Get Current User ====================
  
  /// Get current Firebase user
  User? getCurrentFirebaseUser() {
    return _firebaseAuth.currentUser;
  }
  
  /// Check if user is authenticated
  bool isAuthenticated() {
    return _firebaseAuth.currentUser != null;
  }
}
