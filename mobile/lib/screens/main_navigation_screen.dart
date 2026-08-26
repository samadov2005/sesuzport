import 'package:flutter/material.dart';
import '../constants/app_colors.dart';
import '../constants/theme_notifier.dart';
import 'home/home_screen.dart';
import 'stores/stores_map_screen.dart';
import 'complaint/complaints_list_screen.dart';
import 'complaint/live_camera_screen.dart';
import 'cashback/cashback_screen.dart';
import 'rights/rights_screen.dart';
import 'support/support_screen.dart';
import 'admin/admin_dashboard_screen.dart';
import 'auth/login_screen.dart';
import '../services/api_service.dart';
import '../models/user_model.dart';

class MainNavigationScreen extends StatefulWidget {
  const MainNavigationScreen({super.key});

  @override
  State<MainNavigationScreen> createState() => _MainNavigationScreenState();
}

class _MainNavigationScreenState extends State<MainNavigationScreen> {
  int _currentIndex = 0;

  final List<Widget> _screens = const [
    HomeScreen(),
    StoresMapScreen(),
    ComplaintsListScreen(),
    CashbackScreen(),
    _MoreMenuScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final surfaceColor = isDark ? AppColors.darkSurface : AppColors.lightSurface;
    final navUnselectedColor = isDark ? AppColors.darkTextMuted : AppColors.lightTextMuted;

    return Scaffold(
      backgroundColor: isDark ? AppColors.darkBackground : AppColors.lightBackground,
      body: IndexedStack(
        index: _currentIndex,
        children: _screens,
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          Navigator.of(context).push(
            MaterialPageRoute(builder: (_) => const LiveCameraScreen()),
          );
        },
        backgroundColor: AppColors.primaryLight,
        elevation: 6,
        child: const Icon(Icons.camera_alt_rounded, color: Colors.white, size: 28),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,
      bottomNavigationBar: BottomAppBar(
        color: surfaceColor,
        shape: const CircularNotchedRectangle(),
        notchMargin: 8,
        elevation: 10,
        child: SizedBox(
          height: 60,
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildNavItem(icon: Icons.home_rounded, label: 'Asosiy', index: 0, unselectedColor: navUnselectedColor),
              _buildNavItem(icon: Icons.storefront_rounded, label: 'Do\'konlar', index: 1, unselectedColor: navUnselectedColor),
              const SizedBox(width: 48), // Gap for central FAB
              _buildNavItem(icon: Icons.assignment_rounded, label: 'Murojaat', index: 2, unselectedColor: navUnselectedColor),
              _buildNavItem(icon: Icons.menu_rounded, label: 'Menyu', index: 4, unselectedColor: navUnselectedColor),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildNavItem({
    required IconData icon,
    required String label,
    required int index,
    required Color unselectedColor,
  }) {
    final isSelected = _currentIndex == index;
    final color = isSelected ? AppColors.primaryLight : unselectedColor;

    return InkWell(
      onTap: () => setState(() => _currentIndex = index),
      borderRadius: BorderRadius.circular(16),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, color: color, size: 22),
            const SizedBox(height: 2),
            Text(
              label,
              style: TextStyle(
                fontSize: 10,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                color: color,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _MoreMenuScreen extends StatefulWidget {
  const _MoreMenuScreen();

  @override
  State<_MoreMenuScreen> createState() => _MoreMenuScreenState();
}

class _MoreMenuScreenState extends State<_MoreMenuScreen> {
  UserModel? _user;

  @override
  void initState() {
    super.initState();
    _loadUser();
  }

  Future<void> _loadUser() async {
    final user = await ApiService.getProfile();
    if (mounted) setState(() => _user = user);
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final surfaceColor = isDark ? AppColors.darkSurface : AppColors.lightSurface;
    final borderColor = isDark ? AppColors.darkSurfaceLight : AppColors.lightSurfaceLight;
    final textPrimary = isDark ? AppColors.darkTextPrimary : AppColors.lightTextPrimary;
    final textSecondary = isDark ? AppColors.darkTextSecondary : AppColors.lightTextSecondary;

    final isAdmin = _user?.role == 'ADMIN' || _user?.role == 'MODERATOR';

    return Scaffold(
      backgroundColor: isDark ? AppColors.darkBackground : AppColors.lightBackground,
      appBar: AppBar(
        backgroundColor: surfaceColor,
        elevation: 0,
        title: Text(
          'Qo\'shimcha xizmatlar va Sozlamalar',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: textPrimary),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          // Theme Switcher Card (Yorug' / Tungi rejim)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: surfaceColor,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: borderColor),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: isDark ? AppColors.warnYellow.withOpacity(0.15) : AppColors.infoBlue.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Icon(
                        isDark ? Icons.dark_mode_rounded : Icons.light_mode_rounded,
                        color: isDark ? AppColors.warnYellow : AppColors.infoBlue,
                        size: 22,
                      ),
                    ),
                    const SizedBox(width: 14),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          isDark ? 'Tungi rejim (Dark)' : 'Yorug\' rejim (Light)',
                          style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: textPrimary),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          isDark ? 'Ko\'zga qulay qorong\'i fon' : 'Klassik yorug\' dizayn',
                          style: TextStyle(fontSize: 11, color: textSecondary),
                        ),
                      ],
                    ),
                  ],
                ),
                Switch.adaptive(
                  value: isDark,
                  activeColor: AppColors.primaryLight,
                  onChanged: (val) {
                    ThemeNotifier.instance.toggleTheme(val);
                  },
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),

          // Admin Dashboard Button (if Admin or Moderator)
          if (isAdmin) ...[
            Container(
              decoration: BoxDecoration(
                gradient: AppColors.primaryGradient,
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: AppColors.primary.withOpacity(0.3),
                    blurRadius: 10,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: ListTile(
                leading: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(Icons.admin_panel_settings_rounded, color: Colors.white, size: 24),
                ),
                title: const Text(
                  '🛡 SESPORT Admin Paneli',
                  style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Colors.white),
                ),
                subtitle: const Text(
                  'Murojaatlarni tekshirish va moderatsiya qilish',
                  style: TextStyle(fontSize: 11, color: Colors.white70),
                ),
                trailing: const Icon(Icons.arrow_forward_ios, color: Colors.white, size: 14),
                onTap: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(builder: (_) => const AdminDashboardScreen()),
                  );
                },
              ),
            ),
            const SizedBox(height: 14),
          ],

          _buildMenuItem(
            context,
            surfaceColor: surfaceColor,
            borderColor: borderColor,
            textPrimary: textPrimary,
            icon: Icons.stars_rounded,
            color: AppColors.warnYellow,
            title: 'Keshbek va ballarim',
            onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const CashbackScreen())),
          ),
          const SizedBox(height: 12),
          _buildMenuItem(
            context,
            surfaceColor: surfaceColor,
            borderColor: borderColor,
            textPrimary: textPrimary,
            icon: Icons.balance_rounded,
            color: AppColors.infoBlue,
            title: 'Iste\'molchi huquqlari',
            onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const RightsScreen())),
          ),
          const SizedBox(height: 12),
          _buildMenuItem(
            context,
            surfaceColor: surfaceColor,
            borderColor: borderColor,
            textPrimary: textPrimary,
            icon: Icons.headset_mic_rounded,
            color: AppColors.safeGreen,
            title: 'Yordam va Aloqa (1080)',
            onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const SupportScreen())),
          ),
          const SizedBox(height: 28),
          _buildMenuItem(
            context,
            surfaceColor: surfaceColor,
            borderColor: borderColor,
            textPrimary: textPrimary,
            icon: Icons.logout_rounded,
            color: AppColors.dangerRed,
            title: 'Chiqish (Akkauntdan)',
            onTap: () async {
              await ApiService.clearToken();
              if (context.mounted) {
                Navigator.of(context).pushAndRemoveUntil(
                  MaterialPageRoute(builder: (_) => const LoginScreen()),
                  (route) => false,
                );
              }
            },
          ),
        ],
      ),
    );
  }

  Widget _buildMenuItem(
    BuildContext context, {
    required Color surfaceColor,
    required Color borderColor,
    required Color textPrimary,
    required IconData icon,
    required Color color,
    required String title,
    required VoidCallback onTap,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: surfaceColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: borderColor),
      ),
      child: ListTile(
        leading: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: color.withOpacity(0.15),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(icon, color: color, size: 22),
        ),
        title: Text(title, style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: textPrimary)),
        trailing: const Icon(Icons.arrow_forward_ios, color: AppColors.textMuted, size: 14),
        onTap: onTap,
      ),
    );
  }
}
