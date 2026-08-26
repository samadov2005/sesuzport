import 'package:flutter/material.dart';
import '../constants/app_colors.dart';
import 'home/home_screen.dart';
import 'stores/stores_map_screen.dart';
import 'complaint/complaints_list_screen.dart';
import 'complaint/live_camera_screen.dart';
import 'cashback/cashback_screen.dart';
import 'rights/rights_screen.dart';
import 'support/support_screen.dart';
import 'auth/login_screen.dart';
import '../services/api_service.dart';

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
    return Scaffold(
      backgroundColor: AppColors.background,
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
        color: AppColors.surface,
        shape: const CircularNotchedRectangle(),
        notchMargin: 8,
        elevation: 10,
        child: SizedBox(
          height: 60,
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildNavItem(icon: Icons.home_rounded, label: 'Asosiy', index: 0),
              _buildNavItem(icon: Icons.storefront_rounded, label: 'Do\'konlar', index: 1),
              const SizedBox(width: 48), // Gap for central FAB
              _buildNavItem(icon: Icons.assignment_rounded, label: 'Murojaat', index: 2),
              _buildNavItem(icon: Icons.menu_rounded, label: 'Menyu', index: 4),
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
  }) {
    final isSelected = _currentIndex == index;
    final color = isSelected ? AppColors.primaryLight : AppColors.textMuted;

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

class _MoreMenuScreen extends StatelessWidget {
  const _MoreMenuScreen();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.surface,
        elevation: 0,
        title: const Text('Qo\'shimcha xizmatlar', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          _buildMenuItem(
            context,
            icon: Icons.stars_rounded,
            color: AppColors.warnYellow,
            title: 'Keshbek va ballarim',
            onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const CashbackScreen())),
          ),
          const SizedBox(height: 12),
          _buildMenuItem(
            context,
            icon: Icons.balance_rounded,
            color: AppColors.infoBlue,
            title: 'Iste\'molchi huquqlari',
            onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const RightsScreen())),
          ),
          const SizedBox(height: 12),
          _buildMenuItem(
            context,
            icon: Icons.headset_mic_rounded,
            color: AppColors.safeGreen,
            title: 'Yordam va Aloqa (1080)',
            onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const SupportScreen())),
          ),
          const SizedBox(height: 28),
          _buildMenuItem(
            context,
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
    required IconData icon,
    required Color color,
    required String title,
    required VoidCallback onTap,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.surfaceLight),
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
        title: Text(title, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
        trailing: const Icon(Icons.arrow_forward_ios, color: AppColors.textMuted, size: 14),
        onTap: onTap,
      ),
    );
  }
}
