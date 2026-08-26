import 'package:flutter/material.dart';
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
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadStores();
  }

  Future<void> _loadStores() async {
    setState(() => _isLoading = true);
    final list = await ApiService.getStores(
      status: _selectedStatus,
      query: _searchController.text.trim(),
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
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.surface,
        elevation: 0,
        title: const Text(
          'Do\'konlar va Xavfsizlik Reytingi',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
        ),
      ),
      body: Column(
        children: [
          // Search & Filter Header
          Container(
            padding: const EdgeInsets.all(16),
            color: AppColors.surface,
            child: Column(
              children: [
                // Search Input
                TextField(
                  controller: _searchController,
                  onSubmitted: (_) => _loadStores(),
                  style: const TextStyle(color: AppColors.textPrimary, fontSize: 14),
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
                    fillColor: AppColors.background,
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
                      _buildFilterChip(null, 'Barchasi'),
                      const SizedBox(width: 8),
                      _buildFilterChip('GREEN', '🟢 Yashil (Xavfsiz)'),
                      const SizedBox(width: 8),
                      _buildFilterChip('YELLOW', '🟡 Sariq (Diqqat)'),
                      const SizedBox(width: 8),
                      _buildFilterChip('RED', '🔴 Qizil (Xavfli)'),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // Stores List
          Expanded(
            child: RefreshIndicator(
              onRefresh: _loadStores,
              color: AppColors.primaryLight,
              backgroundColor: AppColors.surface,
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
                                color: AppColors.surface,
                                borderRadius: BorderRadius.circular(16),
                                border: Border.all(color: AppColors.surfaceLight),
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  // Name and Rating Row
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      Expanded(
                                        child: Text(
                                          store.name,
                                          style: const TextStyle(
                                            fontSize: 15,
                                            fontWeight: FontWeight.bold,
                                            color: AppColors.textPrimary,
                                          ),
                                        ),
                                      ),
                                      Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                        decoration: BoxDecoration(
                                          color: safetyColor.withOpacity(0.2),
                                          borderRadius: BorderRadius.circular(8),
                                          border: Border.all(color: safetyColor.withOpacity(0.5)),
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
                                  const SizedBox(height: 6),

                                  // Address
                                  Text(
                                    store.address,
                                    style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
                                  ),
                                  const SizedBox(height: 12),

                                  // Action Buttons (Map, Phone)
                                  Row(
                                    children: [
                                      if (store.latitude != null && store.longitude != null)
                                        OutlinedButton.icon(
                                          onPressed: () => _openMap(store.latitude, store.longitude),
                                          icon: const Icon(Icons.map_outlined, size: 16, color: AppColors.primaryLight),
                                          label: const Text('Xaritada ochish', style: TextStyle(fontSize: 12, color: AppColors.primaryLight)),
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

  Widget _buildFilterChip(String? status, String label) {
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
      backgroundColor: AppColors.background,
      labelStyle: TextStyle(
        color: isSelected ? Colors.white : AppColors.textSecondary,
        fontSize: 12,
        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
      ),
    );
  }
}
