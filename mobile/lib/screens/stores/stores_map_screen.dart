import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../constants/app_colors.dart';
import '../../models/store_model.dart';
import '../../services/api_service.dart';

class StoresMapScreen extends StatefulWidget {
  const StoresMapScreen({super.key});

  @override
  State<StoresMapScreen> createState() => _StoresMapScreenState();
}

class _StoresMapScreenState extends State<StoresMapScreen> {
  List<StoreModel> _stores = [];
  String? _selectedStatus;
  final _searchController = TextEditingController();
  double? _userLat;
  double? _userLng;
  bool _isGettingLocation = false;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _getUserLocationAndLoadStores();
  }

  Future<void> _getUserLocationAndLoadStores() async {
    setState(() => _isGettingLocation = true);
    try {
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (serviceEnabled) {
        LocationPermission permission = await Geolocator.checkPermission();
        if (permission == LocationPermission.denied) {
          permission = await Geolocator.requestPermission();
        }
        if (permission == LocationPermission.whileInUse || permission == LocationPermission.always) {
          Position position = await Geolocator.getCurrentPosition(
            desiredAccuracy: LocationAccuracy.medium,
            timeLimit: const Duration(seconds: 5),
          );
          _userLat = position.latitude;
          _userLng = position.longitude;
        }
      }
    } catch (_) {}

    setState(() => _isGettingLocation = false);
    await _loadStores();
  }

  Future<void> _loadStores() async {
    setState(() => _isLoading = true);
    final list = await ApiService.getStores(
      status: _selectedStatus,
      query: _searchController.text.trim(),
      lat: _userLat,
      lng: _userLng,
    );
    setState(() {
      _stores = list;
      _isLoading = false;
    });
  }

  Color _getSafetyColor(String status) {
    switch (status) {
      case 'GREEN':
        return AppColors.safeGreen;
      case 'YELLOW':
        return AppColors.warnYellow;
      case 'RED':
        return AppColors.dangerRed;
      default:
        return AppColors.safeGreen;
    }
  }

  Future<void> _openMap(double? lat, double? lon) async {
    if (lat == null || lon == null) return;
    final uri = Uri.parse('https://www.google.com/maps/search/?api=1&query=$lat,$lon');
    try {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } catch (_) {}
  }

  Future<void> _makeCall(String phone) async {
    if (phone.isEmpty) return;
    final uri = Uri.parse('tel:$phone');
    try {
      await launchUrl(uri);
    } catch (_) {}
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final surfaceColor = isDark ? AppColors.darkSurface : AppColors.lightSurface;
    final borderColor = isDark ? AppColors.darkSurfaceLight : AppColors.lightSurfaceLight;
    final textPrimary = isDark ? AppColors.darkTextPrimary : AppColors.lightTextPrimary;
    final textSecondary = isDark ? AppColors.darkTextSecondary : AppColors.lightTextSecondary;

    return Scaffold(
      backgroundColor: isDark ? AppColors.darkBackground : AppColors.lightBackground,
      appBar: AppBar(
        backgroundColor: surfaceColor,
        elevation: 0,
        title: Text(
          'Do\'konlar va Xavfsizlik Reytingi',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: textPrimary),
        ),
        actions: [
          IconButton(
            tooltip: 'Joylashuvni yangilash',
            icon: _isGettingLocation
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.primaryLight),
                  )
                : const Icon(Icons.my_location_rounded, color: AppColors.primaryLight),
            onPressed: _getUserLocationAndLoadStores,
          ),
        ],
      ),
      body: Column(
        children: [
          // Search & Filter Header
          Container(
            padding: const EdgeInsets.all(16),
            color: surfaceColor,
            child: Column(
              children: [
                // Search Input
                TextField(
                  controller: _searchController,
                  onSubmitted: (_) => _loadStores(),
                  style: TextStyle(color: textPrimary, fontSize: 14),
                  decoration: InputDecoration(
                    hintText: 'Do\'kon nomi yoki manzil bo\'yicha qidiruv...',
                    hintStyle: const TextStyle(color: AppColors.textMuted, fontSize: 13),
                    prefixIcon: const Icon(Icons.search, color: AppColors.primaryLight, size: 20),
                    suffixIcon: _searchController.text.isNotEmpty
                        ? IconButton(
                            icon: const Icon(Icons.clear, size: 18, color: AppColors.textMuted),
                            onPressed: () {
                              _searchController.clear();
                              _loadStores();
                            },
                          )
                        : null,
                    filled: true,
                    fillColor: isDark ? AppColors.darkBackground : AppColors.lightBackground,
                    contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
                  ),
                ),
                const SizedBox(height: 12),

                // Status Filter Chips
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Row(
                    children: [
                      _buildFilterChip(null, 'Barchasi', isDark),
                      const SizedBox(width: 8),
                      _buildFilterChip('GREEN', '🟢 Yashil (Xavfsiz)', isDark),
                      const SizedBox(width: 8),
                      _buildFilterChip('YELLOW', '🟡 Sariq (Diqqat)', isDark),
                      const SizedBox(width: 8),
                      _buildFilterChip('RED', '🔴 Qizil (Xavfli)', isDark),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // GPS Info Banner if Location Detected
          if (_userLat != null && _userLng != null)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              color: AppColors.primary.withOpacity(0.12),
              child: Row(
                children: [
                  const Icon(Icons.near_me_rounded, color: AppColors.primaryLight, size: 16),
                  const SizedBox(width: 8),
                  Text(
                    'Do\'konlar sizga eng yaqin masofadan saralandi',
                    style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: textPrimary),
                  ),
                ],
              ),
            ),

          // Stores List
          Expanded(
            child: RefreshIndicator(
              onRefresh: _getUserLocationAndLoadStores,
              color: AppColors.primaryLight,
              backgroundColor: surfaceColor,
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator(color: AppColors.primaryLight))
                  : _stores.isEmpty
                      ? const Center(
                          child: Text(
                            'Do\'konlar topilmadi.',
                            style: TextStyle(color: AppColors.textMuted),
                          ),
                        )
                      : ListView.builder(
                          padding: const EdgeInsets.all(16),
                          itemCount: _stores.length,
                          itemBuilder: (context, index) {
                            final store = _stores[index];
                            final safetyColor = _getSafetyColor(store.safetyStatus);

                            return Container(
                              margin: const EdgeInsets.only(bottom: 12),
                              padding: const EdgeInsets.all(16),
                              decoration: BoxDecoration(
                                color: surfaceColor,
                                borderRadius: BorderRadius.circular(16),
                                border: Border.all(color: borderColor),
                                boxShadow: [
                                  if (!isDark)
                                    BoxShadow(
                                      color: Colors.black.withOpacity(0.04),
                                      blurRadius: 8,
                                      offset: const Offset(0, 2),
                                    ),
                                ],
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  // Name, Rating and Distance
                                  Row(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      Expanded(
                                        child: Column(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            Text(
                                              store.name,
                                              style: TextStyle(
                                                fontSize: 15,
                                                fontWeight: FontWeight.bold,
                                                color: textPrimary,
                                              ),
                                            ),
                                            const SizedBox(height: 4),
                                            if (store.distanceKm != null)
                                              Container(
                                                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                                decoration: BoxDecoration(
                                                  color: AppColors.primary.withOpacity(0.15),
                                                  borderRadius: BorderRadius.circular(6),
                                                ),
                                                child: Row(
                                                  mainAxisSize: MainAxisSize.min,
                                                  children: [
                                                    const Icon(Icons.directions_walk_rounded, color: AppColors.primaryLight, size: 12),
                                                    const SizedBox(width: 3),
                                                    Text(
                                                      store.distanceKm! < 1.0
                                                          ? '${(store.distanceKm! * 1000).toInt()} m yaqinlikda'
                                                          : '${store.distanceKm!.toStringAsFixed(1)} km yaqinlikda',
                                                      style: const TextStyle(
                                                        fontSize: 11,
                                                        fontWeight: FontWeight.bold,
                                                        color: AppColors.primaryLight,
                                                      ),
                                                    ),
                                                  ],
                                                ),
                                              ),
                                          ],
                                        ),
                                      ),
                                      const SizedBox(width: 8),
                                      Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                        decoration: BoxDecoration(
                                          color: safetyColor.withOpacity(0.15),
                                          borderRadius: BorderRadius.circular(8),
                                          border: Border.all(color: safetyColor.withOpacity(0.4)),
                                        ),
                                        child: Text(
                                          store.safetyStatusDisplay,
                                          style: TextStyle(
                                            fontSize: 11,
                                            fontWeight: FontWeight.bold,
                                            color: safetyColor,
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 8),

                                  // Address
                                  Row(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      const Icon(Icons.location_on_outlined, size: 14, color: AppColors.textMuted),
                                      const SizedBox(width: 4),
                                      Expanded(
                                        child: Text(
                                          store.address,
                                          style: TextStyle(fontSize: 12, color: textSecondary),
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 12),

                                  // Action Buttons (Map, Phone)
                                  Row(
                                    children: [
                                      if (store.latitude != null && store.longitude != null)
                                        OutlinedButton.icon(
                                          onPressed: () => _openMap(store.latitude, store.longitude),
                                          icon: const Icon(Icons.directions_rounded, size: 16, color: AppColors.primaryLight),
                                          label: const Text('Marshrut / Xarita', style: TextStyle(fontSize: 12, color: AppColors.primaryLight, fontWeight: FontWeight.bold)),
                                          style: OutlinedButton.styleFrom(
                                            side: BorderSide(color: AppColors.primaryLight.withOpacity(0.5)),
                                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                                          ),
                                        ),
                                      const SizedBox(width: 8),
                                      if (store.phone.isNotEmpty)
                                        IconButton(
                                          onPressed: () => _makeCall(store.phone),
                                          icon: const Icon(Icons.phone_outlined, size: 18, color: AppColors.safeGreen),
                                          padding: EdgeInsets.zero,
                                          constraints: const BoxConstraints(),
                                        ),
                                    ],
                                  ),
                                ],
                              ),
                            );
                          },
                        ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFilterChip(String? status, String label, bool isDark) {
    final isSelected = _selectedStatus == status;
    return ChoiceChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (selected) {
        if (selected) {
          setState(() => _selectedStatus = status);
          _loadStores();
        }
      },
      selectedColor: AppColors.primary,
      backgroundColor: isDark ? AppColors.darkBackground : AppColors.lightBackground,
      labelStyle: TextStyle(
        color: isSelected ? Colors.white : (isDark ? AppColors.darkTextSecondary : AppColors.lightTextSecondary),
        fontSize: 12,
        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
      ),
    );
  }
}
