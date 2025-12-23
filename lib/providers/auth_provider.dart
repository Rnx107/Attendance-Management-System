/// Authentication Provider for State Management
///
/// This provider manages the authentication state across the app using
/// ChangeNotifier pattern. It exposes methods for authentication operations
/// and notifies listeners of state changes.

import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../services/auth_service.dart';
import '../services/storage_service.dart';

/// Authentication status enum
enum AuthStatus {
  uninitialized,
  authenticated,
  unauthenticated,
  authenticating,
}

class AuthProvider with ChangeNotifier {
  final AuthService _authService = AuthService();
  final StorageService _storage = StorageService();
  final FirebaseAuth _firebaseAuth = FirebaseAuth.instance;
  
  AuthStatus _status = AuthStatus.uninitialized;
  Map<String, dynamic>? _userData;
  String? _errorMessage;
  User? _firebaseUser;
  
  // Getters
  AuthStatus get status => _status;
  Map<String, dynamic>? get userData => _userData;
  String? get errorMessage => _errorMessage;
  User? get firebaseUser => _firebaseUser;
  bool get isAuthenticated => _status == AuthStatus.authenticated;
  bool get isLoading => _status == AuthStatus.authenticating;
  
  // User info getters
  String? get userEmail => _userData?['email'];
  String? get userFirstname => _userData?['firstname'];
  String? get userLastname => _userData?['lastname'];
  String? get userRole => _userData?['role'];
  String get userFullName {
    if (_userData == null) return '';
    final firstname = _userData!['firstname'] ?? '';
    final lastname = _userData!['lastname'] ?? '';
    return '$firstname $lastname'.trim();
  }
  
  // Constructor
  AuthProvider() {
    _initializeAuth();
  }
  
  // ==================== Initialization ====================
  
  /// Initialize authentication state
  Future<void> _initializeAuth() async {
    try {
      // Listen to Firebase auth state changes
      _firebaseAuth.authStateChanges().listen(_onAuthStateChanged);
      
      // Check for existing session
      await _checkExistingSession();
    } catch (e) {
      _status = AuthStatus.unauthenticated;
      _errorMessage = 'Initialization failed: $e';
      notifyListeners();
    }
  }
  
  /// Handle Firebase auth state changes
  Future<void> _onAuthStateChanged(User? user) async {
    _firebaseUser = user;
    
    if (user == null) {
      // User signed out
      if (_status != AuthStatus.uninitialized) {
        _status = AuthStatus.unauthenticated;
        _userData = null;
        notifyListeners();
      }
    } else {
      // User signed in, verify session with backend
      await _checkExistingSession();
    }
  }
  
  /// Check for existing valid session
  Future<void> _checkExistingSession() async {
    try {
      final hasValidSession = await _storage.hasValidSession();
      
      if (hasValidSession) {
        // Load user data from storage
        final email = await _storage.getUserEmail();
        final firstname = await _storage.getUserFirstname();
        final lastname = await _storage.getUserLastname();
        final role = await _storage.getUserRole();
        
        if (email != null) {
          _userData = {
            'email': email,
            'firstname': firstname ?? '',
            'lastname': lastname ?? '',
            'role': role ?? 'student',
          };
          _status = AuthStatus.authenticated;
          notifyListeners();
          return;
        }
      }
      
      // No valid session
      if (_status == AuthStatus.uninitialized) {
        _status = AuthStatus.unauthenticated;
        notifyListeners();
      }
    } catch (e) {
      _status = AuthStatus.unauthenticated;
      notifyListeners();
    }
  }
  
  // ==================== Sign In ====================
  
  /// Sign in with Google
  Future<bool> signInWithGoogle() async {
    try {
      _status = AuthStatus.authenticating;
      _errorMessage = null;
      notifyListeners();
      
      final result = await _authService.signInWithGoogle();
      
      if (result['success'] == true) {
        _userData = result['user'];
        _status = AuthStatus.authenticated;
        _errorMessage = null;
        notifyListeners();
        return true;
      } else {
        _status = AuthStatus.unauthenticated;
        _errorMessage = result['message'] ?? 'Sign-in failed';
        notifyListeners();
        return false;
      }
    } catch (e) {
      _status = AuthStatus.unauthenticated;
      _errorMessage = 'Sign-in failed: $e';
      notifyListeners();
      return false;
    }
  }
  
  // ==================== Sign Out ====================
  
  /// Sign out from all services
  Future<bool> signOut() async {
    try {
      final result = await _authService.signOut();
      
      if (result['success'] == true) {
        _status = AuthStatus.unauthenticated;
        _userData = null;
        _firebaseUser = null;
        _errorMessage = null;
        notifyListeners();
        return true;
      } else {
        _errorMessage = result['message'] ?? 'Sign-out failed';
        notifyListeners();
        return false;
      }
    } catch (e) {
      _errorMessage = 'Sign-out failed: $e';
      notifyListeners();
      return false;
    }
  }
  
  // ==================== Refresh Token ====================
  
  /// Refresh session token
  Future<bool> refreshToken() async {
    try {
      final result = await _authService.refreshSessionToken();
      
      if (result['success'] == true) {
        // Token refreshed successfully
        return true;
      } else {
        _errorMessage = result['message'] ?? 'Token refresh failed';
        notifyListeners();
        return false;
      }
    } catch (e) {
      _errorMessage = 'Token refresh failed: $e';
      notifyListeners();
      return false;
    }
  }
  
  // ==================== Verify Session ====================
  
  /// Verify current session
  Future<bool> verifySession() async {
    try {
      final result = await _authService.verifySession();
      
      if (result['success'] == true && result['valid'] == true) {
        // Update user data if available
        if (result['user'] != null) {
          _userData = result['user'];
          _status = AuthStatus.authenticated;
          notifyListeners();
        }
        return true;
      } else {
        // Session invalid, sign out
        await signOut();
        return false;
      }
    } catch (e) {
      _errorMessage = 'Session verification failed: $e';
      notifyListeners();
      return false;
    }
  }
  
  // ==================== Error Handling ====================
  
  /// Clear error message
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }
  
  /// Set error message
  void setError(String message) {
    _errorMessage = message;
    notifyListeners();
  }
}
