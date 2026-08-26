import 'package:flutter/material.dart';
import '../../constants/app_colors.dart';
import '../../services/api_service.dart';
import '../main_navigation_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _phoneController = TextEditingController(text: '+998');
  final _nameController = TextEditingController();
  bool _isLoading = false;
  String? _errorMessage;

  Future<void> _handleLogin() async {
    final phone = _phoneController.text.trim();
    final name = _nameController.text.trim();

    if (phone.length < 9) {
      setState(() => _errorMessage = "To'g'ri telefon raqam kiriting.");
      return;
    }

    if (name.isEmpty) {
      setState(() => _errorMessage = "Iltimos, ism-familiyangizni kiriting.");
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final result = await ApiService.login(
      phoneNumber: phone,
      fullName: name,
    );

    setState(() => _isLoading = false);

    if (result['success'] == true) {
      if (!mounted) return;
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => const MainNavigationScreen()),
      );
    } else {
      setState(() => _errorMessage = result['error'] ?? "Xatolik yuz berdi.");
    }
  }

  @override
  void dispose() {
    _phoneController.dispose();
    _nameController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final c = context.colors;

    return Scaffold(
      backgroundColor: c.background,
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Logo & Shield Icon
                Container(
                  width: 72,
                  height: 72,
                  decoration: BoxDecoration(
                    gradient: AppColors.primaryGradient,
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: AppColors.primary.withOpacity(0.3),
                        blurRadius: 16,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: const Icon(Icons.shield_outlined, size: 36, color: Colors.white),
                ),
                const SizedBox(height: 20),

                // Title
                Text(
                  'SESPORT',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 26,
                    fontWeight: FontWeight.w900,
                    letterSpacing: 2,
                    color: c.textPrimary,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  'Sanitariya xavfsizligi va iste\'molchilar himoyasi',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 12,
                    color: c.textSecondary,
                  ),
                ),
                const SizedBox(height: 36),

                // Form Container Card
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: c.surface,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: c.surfaceLight),
                    boxShadow: c.cardShadow,
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Ism va Familiya',
                        style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: c.textPrimary),
                      ),
                      const SizedBox(height: 8),
                      TextField(
                        controller: _nameController,
                        style: TextStyle(color: c.textPrimary),
                        decoration: InputDecoration(
                          hintText: 'Avazbek Samadov',
                          hintStyle: TextStyle(color: c.textMuted, fontSize: 13),
                          prefixIcon: const Icon(Icons.person_outline, color: AppColors.primaryLight, size: 20),
                          filled: true,
                          fillColor: c.background,
                          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: c.surfaceLight)),
                          enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: c.surfaceLight)),
                        ),
                      ),
                      const SizedBox(height: 16),

                      Text(
                        'Telefon raqamingiz',
                        style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: c.textPrimary),
                      ),
                      const SizedBox(height: 8),
                      TextField(
                        controller: _phoneController,
                        keyboardType: TextInputType.phone,
                        style: TextStyle(color: c.textPrimary),
                        decoration: InputDecoration(
                          hintText: '+998 90 123 45 67',
                          hintStyle: TextStyle(color: c.textMuted, fontSize: 13),
                          prefixIcon: const Icon(Icons.phone_outlined, color: AppColors.primaryLight, size: 20),
                          filled: true,
                          fillColor: c.background,
                          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: c.surfaceLight)),
                          enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: c.surfaceLight)),
                        ),
                      ),
                      const SizedBox(height: 20),

                      // Error message if any
                      if (_errorMessage != null) ...[
                        Text(
                          _errorMessage!,
                          style: const TextStyle(color: AppColors.dangerRed, fontSize: 12),
                        ),
                        const SizedBox(height: 12),
                      ],

                      // Submit Button
                      SizedBox(
                        width: double.infinity,
                        height: 48,
                        child: ElevatedButton(
                          onPressed: _isLoading ? null : _handleLogin,
                          style: ElevatedButton.styleFrom(
                            padding: EdgeInsets.zero,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                          ),
                          child: Ink(
                            decoration: BoxDecoration(
                              gradient: AppColors.primaryGradient,
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Center(
                              child: _isLoading
                                  ? const SizedBox(
                                      width: 20,
                                      height: 20,
                                      child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                                    )
                                  : const Text(
                                      'Kirish / Ro\'yxatdan o\'tish',
                                      style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.white),
                                    ),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),

                // Footer Note
                Text(
                  'Kirish orqali xavfsizlik va maxfiylik shartlariga rozilik bildirasiz.',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 11, color: c.textMuted),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
