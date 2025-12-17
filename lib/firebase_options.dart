import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/foundation.dart'
    show defaultTargetPlatform, kIsWeb, TargetPlatform;

/// Default [FirebaseOptions] for use with your Firebase apps.
///
/// Example:
/// ```dart
/// import 'firebase_options.dart';
/// // ...
/// await Firebase.initializeApp(
///   options: DefaultFirebaseOptions.currentPlatform,
/// );
/// ``
class DefaultFirebaseOptions {
  static FirebaseOptions get currentPlatform {
    if (kIsWeb) {
      return web;
    }
    switch (defaultTargetPlatform) {
      case TargetPlatform.android:
        return android;
      case TargetPlatform.iOS:
        return ios;
      case TargetPlatform.macOS:
        return macos;
      case TargetPlatform.windows:
        return windows;
      case TargetPlatform.linux:
        throw UnsupportedError(
          'DefaultFirebaseOptions have not been configured for linux - '
          'you can reconfigure this by running the FlutterFire CLI again.',
        );
      default:
        throw UnsupportedError(
          'DefaultFirebaseOptions are not supported for this platform.',
        );
    }
  }

  static const FirebaseOptions web = FirebaseOptions(
    apiKey: 'AIzaSyCOEXjajtsQKo7f_1wcPTQLyo_2SZk6PK4',
    appId: '1:984567447986:web:967752e8a09980899fa4ab',
    messagingSenderId: '984567447986',
    projectId: 'attendance-management-sy-f0621',
    authDomain: 'attendance-management-sy-f0621.firebaseapp.com',
    storageBucket: 'attendance-management-sy-f0621.firebasestorage.app',
    measurementId: 'G-4NPPDZPC0V',
  );

  static const FirebaseOptions android = FirebaseOptions(
    apiKey: 'AIzaSyAKrUEeYe66KvHHBrDdoFuxxob-O97bMRA',
    appId: '1:984567447986:android:c890bf876d1a526e9fa4ab',
    messagingSenderId: '984567447986',
    projectId: 'attendance-management-sy-f0621',
    storageBucket: 'attendance-management-sy-f0621.firebasestorage.app',
  );

  static const FirebaseOptions ios = FirebaseOptions(
    apiKey: 'AIzaSyA_J_0DWa5--Ia6bejqFA3VSwxD375nVN0',
    appId: '1:984567447986:ios:da2068e7746247e49fa4ab',
    messagingSenderId: '984567447986',
    projectId: 'attendance-management-sy-f0621',
    storageBucket: 'attendance-management-sy-f0621.firebasestorage.app',
    iosClientId: '984567447986-jog26or3pcm9l1jq60ujpr99l5hn0l0v.apps.googleusercontent.com',
    iosBundleId: 'com.example.attendanceManagementSystem',
  );

  static const FirebaseOptions macos = FirebaseOptions(
    apiKey: 'AIzaSyA_J_0DWa5--Ia6bejqFA3VSwxD375nVN0',
    appId: '1:984567447986:ios:da2068e7746247e49fa4ab',
    messagingSenderId: '984567447986',
    projectId: 'attendance-management-sy-f0621',
    storageBucket: 'attendance-management-sy-f0621.firebasestorage.app',
    iosClientId: '984567447986-jog26or3pcm9l1jq60ujpr99l5hn0l0v.apps.googleusercontent.com',
    iosBundleId: 'com.example.attendanceManagementSystem',
  );

  static const FirebaseOptions windows = FirebaseOptions(
    apiKey: 'AIzaSyCOEXjajtsQKo7f_1wcPTQLyo_2SZk6PK4',
    appId: '1:984567447986:web:f74724b79a9d338e9fa4ab',
    messagingSenderId: '984567447986',
    projectId: 'attendance-management-sy-f0621',
    authDomain: 'attendance-management-sy-f0621.firebaseapp.com',
    storageBucket: 'attendance-management-sy-f0621.firebasestorage.app',
    measurementId: 'G-8HPLKX69RD',
  );

}