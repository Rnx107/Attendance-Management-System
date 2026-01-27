import 'package:flutter/material.dart';
import 'package:attendance_management_system/core/constants.dart';
import 'package:attendance_management_system/core/utils.dart';
import 'package:attendance_management_system/pages/signup.dart';
import 'package:attendance_management_system/services/api_services.dart';
// import 'package:attendance_management_system/pages/home.dart';


class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final emailController = TextEditingController();
  final passwordController = TextEditingController();
  bool isLoading = false;

  void _login() async {
    if (emailController.text.isEmpty || passwordController.text.isEmpty) {
      showSnackBar(
        context,
        'Please enter email and password',
        AppColors.errorRed,
      );
      return;
    }

    setState(() => isLoading = true);

    try {
      final response = await ApiService.login(
        email: emailController.text.trim(),
        password: passwordController.text.trim(),
      );

      if (response['success']) {
        showSnackBar(
          context,
          'Login successful!',
          AppColors.successGreen,
        );
        // TODO: Navigate to appropriate dashboard based on user role
        // if (response['role'] == 'student') {
        //   Navigator.pushReplacementNamed(context, '/student_dashboard');
        // } else if (response['role'] == 'teacher') {
        //   Navigator.pushReplacementNamed(context, '/teacher_dashboard');
        // }
      } else {
        showSnackBar(
          context,
          response['error'] ?? 'Login failed',
          AppColors.errorRed,
        );
      }
    } catch (e) {
      showSnackBar(
        context,
        'Error: $e',
        AppColors.errorRed,
      );
    } finally {
      setState(() => isLoading = false);
    }
  }

  @override
  void dispose() {
    emailController.dispose();
    passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min, // make sure the div is centered
            children: [
              // Logo Image
              Image.asset('assets/images/logo.png', height: 120),

              const SizedBox(height: 20), //space between

              const Text(
                'KUSOED Login',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: AppColors.primaryBlue,
                ),
              ),

              const SizedBox(height: 30),

              // Email Field
              TextField(
                controller: emailController,
                decoration: const InputDecoration(
                  labelText: 'Email',
                  border: OutlineInputBorder(),
                ),
              ),

              const SizedBox(height: 15),

              // Password Field
              TextField(
                controller: passwordController,
                obscureText: true,
                decoration: const InputDecoration(
                  labelText: 'Password',
                  border: OutlineInputBorder(),
                ),
              ),

              const SizedBox(height: 25),

              // Login Button
              SizedBox(
                width: double.infinity,
                height: 45,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primaryBlue,
                    foregroundColor: Colors.white,
                  ),
                  onPressed: isLoading ? null : _login,
                  child: isLoading
                      ? const SizedBox(
                          height: 20,
                          width: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor:
                                AlwaysStoppedAnimation<Color>(Colors.white),
                          ),
                        )
                      : const Text('Login'),
                ),
              ),
              TextButton(
                onPressed: () {
                  showSnackBar(
                    context,
                    'Navigating to Register Page',
                    AppColors.warmWheat,
                  );

                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const RegisterPage(),
                    ),
                  );
                },
                child: const Text('Create new account'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}