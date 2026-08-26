import 'package:flutter/material.dart';
import '../../constants/app_colors.dart';
import '../../models/user_model.dart';
import '../../models/store_model.dart';
import '../../services/api_service.dart';
import '../complaint/live_camera_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  UserModel? _user;
  List<StoreModel> _safeStores = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    final user = await ApiService.getProfile();
    final stores = await ApiService.getStores(status: 'GREEN');
    setState(() {
      _user = user;
      _safeStores = stores.take(5).toList();
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final c = context.colors;

    return Scaffold(
      backgroundColor: c.background,
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _loadData,
          color: AppColors.primaryLight,
          backgroundColor: c.surface,
          child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Top Header Profile Row
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Xush kelibsiz! 👋',
                          style: TextStyle(fontSize: 13, color: c.textSecondary),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          _user?.fullName ?? 'Iste\'molchi',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: c.textPrimary,
                          ),
                        ),
                      ],
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: AppColors.primary.withOpacity(0.12),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: AppColors.primaryLight.withOpacity(0.3)),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.stars_rounded, color: AppColors.warnYellow, size: 18),
                          const SizedBox(width: 6),
                          Text(
                            '${_user?.cashbackBalance.toStringAsFixed(0) ?? '0'} ball',
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                              color: c.textPrimary,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),

                // Main CTA: Quick Live Camera Complaint Card
                GestureDetector(
                  onTap: () {
                    Navigator.of(context).push(
                      MaterialPageRoute(builder: (_) => const LiveCameraScreen()),
                    );
                  },
                  child: Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      gradient: AppColors.primaryGradient,
                      borderRadius: BorderRadius.circular(24),
                      boxShadow: [
                        BoxShadow(
                          color: AppColors.primary.withOpacity(0.35),
                          blurRadius: 18,
                          offset: const Offset(0, 8),
                        ),
                      ],
                    ),
                    child: Row(
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: const [
                              Text(
                                'TEZKOR SHIKOYAT',
                                style: TextStyle(
                                  fontSize: 11,
                                  fontWeight: FontWeight.w900,
                                  letterSpacing: 1.5,
                                  color: Colors.white70,
                                ),
                              ),
                              SizedBox(height: 6),
                              Text(
                                '📸 Jonli kamera orqali qoidabuzarlikni yuborish',
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.white,
                                  height: 1.3,
                                ),
                              ),
                              SizedBox(height: 8),
                              Text(
                                'Muddati o\'tgan yoki sifatsiz mahsulotlar',
                                style: TextStyle(fontSize: 12, color: Colors.white70),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(width: 12),
                        Container(
                          width: 56,
                          height: 56,
                          decoration: BoxDecoration(
                            color: Colors.white.withOpacity(0.2),
                            shape: BoxShape.circle,
                          ),
                          child: const Icon(Icons.camera_alt, color: Colors.white, size: 30),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 24),

                // Stats Row
                Row(
                  children: [
                    _buildStatCard(
                      c: c,
                      title: 'Murojaatlarim',
                      value: '${_user?.totalComplaints ?? 0}',
                      icon: Icons.assignment_outlined,
                      color: AppColors.infoBlue,
                    ),
                    const SizedBox(width: 12),
                    _buildStatCard(
                      c: c,
                      title: 'Hal qilingan',
                      value: '${_user?.resolvedComplaints ?? 0}',
                      icon: Icons.check_circle_outline,
                      color: AppColors.safeGreen,
                    ),
                  ],
                ),
                const SizedBox(height: 28),

                // Section Title: Safe Stores
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Xavfsiz do\'konlar (Yashil reyting)',
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                        color: c.textPrimary,
                      ),
                    ),
                    const Text(
                      'Barchasi →',
                      style: TextStyle(fontSize: 12, color: AppColors.primaryLight, fontWeight: FontWeight.w600),
                    ),
                  ],
                ),
                const SizedBox(height: 12),

                // Safe Stores List
                if (_safeStores.isEmpty && !_isLoading)
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: c.surface,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: c.surfaceLight),
                    ),
                    child: Center(
                      child: Text('Do\'konlar ro\'yxati yangilanmoqda...', style: TextStyle(color: c.textMuted)),
                    ),
                  )
                else
                  Column(
                    children: _safeStores.map((store) => _buildStoreItem(store, c)).toList(),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildStatCard({
    required AppThemeColors c,
    required String title,
    required String value,
    required IconData icon,
    required Color color,
  }) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: c.surface,
          borderRadius: BorderRadius.circular(18),
          border: Border.all(color: c.surfaceLight),
          boxShadow: c.cardShadow,
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: color.withOpacity(0.15),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: color, size: 22),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    value,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(fontSize: 17, fontWeight: FontWeight.bold, color: c.textPrimary),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    title,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(fontSize: 11, color: c.textSecondary),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStoreItem(StoreModel store, AppThemeColors c) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: c.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: c.surfaceLight),
        boxShadow: c.cardShadow,
      ),
      child: Row(
        children: [
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: AppColors.safeGreen.withOpacity(0.15),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(Icons.storefront, color: AppColors.safeGreen, size: 24),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  store.name,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: c.textPrimary),
                ),
                const SizedBox(height: 3),
                Text(
                  store.address,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(fontSize: 11, color: c.textSecondary),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: AppColors.safeGreen.withOpacity(0.2),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              children: [
                const Icon(Icons.star, color: AppColors.safeGreen, size: 12),
                const SizedBox(width: 4),
                Text(
                  store.rating.toStringAsFixed(1),
                  style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppColors.safeGreen),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
