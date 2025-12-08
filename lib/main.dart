import 'package:flutter/material.dart';
import 'Pages/markattendance.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,

      // INITIAL PAGE OF THE APP
      home: const AttendanceScreen(),   // <-- ADD SCREEN HERE
    );
  }
}
