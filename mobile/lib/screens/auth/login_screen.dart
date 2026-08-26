import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../constants/app_colors.dart';
import '../../constants/app_strings.dart';
import '../../services/api_service.dart';
import '../main_navigation_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final _phoneController = TextEditingController();
  final _nameController = TextEditingController();
  bool _isLoading = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  String _cleanPhoneNumber(String input) {
    final digitsOnly = input.replaceAll(RegExp(r'\D'), '');
    if (digitsOnly.startsWith('998')) {
      return '+$digitsOnly';
    }
    return '+998$digitsOnly';
  }

  Future<void> _handleSubmit(bool isRegister) async {
    final rawPhone = _phoneController.text.trim();
    final digits = rawPhone.replaceAll(RegExp(r'\D'), '');
    final name = _nameController.text.trim();

    // Check if phone has 9 digits (without 998) or 12 digits (with 998)
    int phoneDigitsCount = digits.startsWith('998') ? digits.length - 3 : digits.length;

    if (phoneDigitsCount != 9) {
      setState(() => _errorMessage = "Telefon raqami 9 ta raqamdan iborat bo'lishi kerak (masalan: 90 123 45 67).");
      return;
    }

    if (isRegister && name.isEmpty) {
      setState(() => _errorMessage = "Iltimos, ism va familiyangizni kiriting.");
      return;
    }

    final formattedPhone = _cleanPhoneNumber(rawPhone);

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final result = await ApiService.login(
      phoneNumber: formattedPhone,
      fullName: name.isNotEmpty ? name : 'Foydalanuvchi',
      language: AppLocaleNotifier.instance.lang,
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
    _tabController.dispose();
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
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Top Language Switcher Bar
                Align(
                  alignment: Alignment.topRight,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: c.surface,
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: c.surfaceLight),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        _buildLangBtn('uz', '🇺🇿 UZ'),
                        _buildLangBtn('ru', '🇷🇺 RU'),
                        _buildLangBtn('en', '🇬🇧 EN'),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),

                // Logo
                Center(
                  child: Container(
                    width: 76,
                    height: 76,
                    decoration: BoxDecoration(
                      gradient: AppColors.primaryGradient,
                      shape: BoxShape.circle,
                      boxShadow: [
                        BoxShadow(
                          color: AppColors.primary.withOpacity(0.35),
                          blurRadius: 18,
                          offset: const Offset(0, 6),
                        ),
                      ],
                    ),
                    child: const Icon(Icons.shield_outlined, size: 40, color: Colors.white),
                  ),
                ),
                const SizedBox(height: 16),

                // Title
                Text(
                  AppStrings.get('app_name'),
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 26,
                    fontWeight: FontWeight.w900,
                    letterSpacing: 2,
                    color: c.textPrimary,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  AppStrings.get('app_subtitle'),
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 12,
                    color: c.textSecondary,
                  ),
                ),
                const SizedBox(height: 28),

                // Card with Tabs (Kirish vs Ro'yxatdan o'tish)
                Container(
                  decoration: BoxDecoration(
                    color: c.surface,
                    borderRadius: BorderRadius.circular(24),
                    border: Border.all(color: c.surfaceLight),
                    boxShadow: c.cardShadow,
                  ),
                  child: Column(
                    children: [
                      // Tab Header
                      Container(
                        margin: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: c.background,
                          borderRadius: BorderRadius.circular(14),
                        ),
                        child: TabBar(
                          controller: _tabController,
                          indicator: BoxDecoration(
                            gradient: AppColors.primaryGradient,
                            borderRadius: BorderRadius.circular(12),
                          ),
                          indicatorSize: TabBarIndicatorSize.tab,
                          dividerColor: Colors.transparent,
                          labelColor: Colors.white,
                          unselectedLabelColor: c.textSecondary,
                          labelStyle: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                          tabs: [
                            Tab(text: AppStrings.get('login')),
                            Tab(text: AppStrings.get('register')),
                          ],
                          onTap: (_) => setState(() => _errorMessage = null),
                        ),
                      ),

                      // Form Content
                      Padding(
                        padding: const EdgeInsets.fromLTRB(20, 8, 20, 24),
                        child: AnimatedBuilder(
                          animation: _tabController,
                          builder: (context, _) {
                            final isRegister = _tabController.index == 1;

                            return Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                // Full Name field for registration
                                if (isRegister) ...[
                                  Text(
                                    AppStrings.get('full_name'),
                                    style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: c.textPrimary),
                                  ),
                                  const SizedBox(height: 6),
                                  TextField(
                                    controller: _nameController,
                                    style: TextStyle(color: c.textPrimary),
                                    decoration: InputDecoration(
                                      hintText: AppStrings.get('full_name_hint'),
                                      hintStyle: TextStyle(color: c.textMuted, fontSize: 13),
                                      prefixIcon: const Icon(Icons.person_outline, color: AppColors.primaryLight, size: 20),
                                      filled: true,
                                      fillColor: c.background,
                                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: c.surfaceLight)),
                                      enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: c.surfaceLight)),
                                    ),
                                  ),
                                  const SizedBox(height: 16),
                                ],

                                // Phone number field
                                Text(
                                  AppStrings.get('phone_number'),
                                  style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: c.textPrimary),
                                ),
                                const SizedBox(height: 6),
                                TextField(
                                  controller: _phoneController,
                                  keyboardType: TextInputType.phone,
                                  inputFormatters: [
                                    FilteringTextInputFormatter.digitsOnly,
                                    LengthLimitingTextInputFormatter(9),
                                  ],
                                  style: TextStyle(color: c.textPrimary, fontWeight: FontWeight.bold),
                                  decoration: InputDecoration(
                                    prefixText: '+998 ',
                                    prefixStyle: TextStyle(color: c.textPrimary, fontWeight: FontWeight.bold),
                                    hintText: '90 123 45 67',
                                    hintStyle: TextStyle(color: c.textMuted, fontSize: 13),
                                    prefixIcon: const Icon(Icons.phone_outlined, color: AppColors.primaryLight, size: 20),
                                    filled: true,
                                    fillColor: c.background,
                                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: c.surfaceLight)),
                                    enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: c.surfaceLight)),
                                  ),
                                ),
                                const SizedBox(height: 20),

                                // Error message
                                if (_errorMessage != null) ...[
                                  Text(
                                    _errorMessage!,
                                    style: const TextStyle(color: AppColors.dangerRed, fontSize: 12),
                                  ),
                                  const SizedBox(height: 12),
                                ],

                                // Action Button
                                SizedBox(
                                  width: double.infinity,
                                  height: 48,
                                  child: ElevatedButton(
                                    onPressed: _isLoading ? null : () => _handleSubmit(isRegister),
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
                                            : Text(
                                                isRegister ? AppStrings.get('register_btn') : AppStrings.get('login_btn'),
                                                style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.white),
                                              ),
                                      ),
                                    ),
                                  ),
                                ),
                              ],
                            );
                          },
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 20),

                // Footer terms
                Text(
                  AppStrings.get('terms_note'),
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

  Widget _buildLangBtn(String langCode, String label) {
    final currentLang = AppLocaleNotifier.instance.lang;
    final isSelected = currentLang == langCode;

    return InkWell(
      onTap: () {
        AppLocaleNotifier.instance.setLanguage(langCode);
        setState(() {});
      },
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: isSelected ? AppColors.primary.withOpacity(0.2) : Colors.transparent,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 11,
            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
            color: isSelected ? AppColors.primaryLight : AppColors.textMuted,
          ),
        ),
      ),
    );
  }
}
