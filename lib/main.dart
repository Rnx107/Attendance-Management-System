import 'package:flutter/material.dart';
import 'Pages/courselist.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: Scaffold(
        appBar: AppBar(
          backgroundColor: Colors.blue,
          title: Text("Hello"),
          leading: Builder(
            builder: (context) => IconButton(
              onPressed: () {},
              icon: Icon(Icons.menu),
            ),
          ),
        ),
      ),
    );
  }
}
