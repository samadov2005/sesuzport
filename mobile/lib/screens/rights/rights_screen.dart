import 'package:flutter/material.dart';
import '../../constants/app_colors.dart';
import '../../services/api_service.dart';

class RightsScreen extends StatefulWidget {
  const RightsScreen({super.key});

  @override
  State<RightsScreen> createState() => _RightsScreenState();
}

class _RightsScreenState extends State<RightsScreen> {
  List<Map<String, dynamic>> _rights = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadRights();
  }

  Future<void> _loadRights() async {
    setState(() => _isLoading = true);
    final list = await ApiService.getRights();
    setState(() {
      _rights = list;
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.surface,
        elevation: 0,
        title: const Text(
          'Iste\'molchi Huquqlari',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AppColors.primaryLight))
          : _rights.isEmpty
              ? const Center(
                  child: Text(
                    'Huquqlar ro\'yxati yangilanmoqda...',
                    style: TextStyle(color: AppColors.textMuted),
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: _rights.length,
                  itemBuilder: (context, index) {
                    final item = _rights[index];

                    return Container(
                      margin: const EdgeInsets.only(bottom: 12),
                      decoration: BoxDecoration(
                        color: AppColors.surface,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: AppColors.surfaceLight),
                      ),
                      child: Theme(
                        data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
                        child: ExpansionTile(
                          iconColor: AppColors.primaryLight,
                          collapsedIconColor: AppColors.textMuted,
                          tilePadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
                          title: Text(
                            item['title'] ?? '',
                            style: const TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.bold,
                              color: AppColors.textPrimary,
                            ),
                          ),
                          subtitle: Padding(
                            padding: const EdgeInsets.only(top: 4),
                            child: Text(
                              item['category'] ?? 'Umumiy',
                              style: const TextStyle(fontSize: 11, color: AppColors.primaryLight),
                            ),
                          ),
                          children: [
                            Padding(
                              padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                              child: Text(
                                item['content'] ?? '',
                                style: const TextStyle(
                                  fontSize: 13,
                                  color: AppColors.textSecondary,
                                  height: 1.4,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
    );
  }
}
