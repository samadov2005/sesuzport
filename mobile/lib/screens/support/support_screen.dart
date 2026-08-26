import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../constants/app_colors.dart';
import '../../services/api_service.dart';

class SupportScreen extends StatefulWidget {
  const SupportScreen({super.key});

  @override
  State<SupportScreen> createState() => _SupportScreenState();
}

class _SupportScreenState extends State<SupportScreen> {
  Map<String, dynamic> _support = {};
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadSupport();
  }

  Future<void> _loadSupport() async {
    setState(() => _isLoading = true);
    final data = await ApiService.getSupportInfo();
    setState(() {
      _support = data;
      _isLoading = false;
    });
  }

  Future<void> _makeCall(String number) async {
    final uri = Uri.parse('tel:$number');
    try {
      await launchUrl(uri);
    } catch (_) {}
  }

  Future<void> _openTelegram(String username) async {
    final uri = Uri.parse('https://t.me/$username');
    try {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    final phone = _support['phone'] ?? '+998712000000';
    final admin = _support['telegram_admin'] ?? 'sesport_admin';
    final dev = _support['developer'] ?? 'samadov2005';
    final faq = (_support['faq'] as List?) ?? [];

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.surface,
        elevation: 0,
        title: const Text(
          'Yordam va Aloqa Markazi',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Contact Buttons Card
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: AppColors.surfaceLight),
              ),
              child: Column(
                children: [
                  _buildContactAction(
                    icon: Icons.phone_in_talk_rounded,
                    color: AppColors.safeGreen,
                    title: 'Ishonch telefoni (1080)',
                    subtitle: phone,
                    onTap: () => _makeCall(phone),
                  ),
                  const Divider(color: AppColors.surfaceLight, height: 24),
                  _buildContactAction(
                    icon: Icons.send_rounded,
                    color: AppColors.infoBlue,
                    title: 'Bosh Administrator',
                    subtitle: '@$admin',
                    onTap: () => _openTelegram(admin),
                  ),
                  const Divider(color: AppColors.surfaceLight, height: 24),
                  _buildContactAction(
                    icon: Icons.code_rounded,
                    color: AppColors.purple,
                    title: 'Dasturchi va Texnik qo\'llab-quvvatlash',
                    subtitle: '@$dev',
                    onTap: () => _openTelegram(dev),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 28),

            // FAQ Section
            const Text(
              'Ko\'p beriladigan savollar (FAQ)',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
            ),
            const SizedBox(height: 12),

            if (_isLoading)
              const Center(child: CircularProgressIndicator(color: AppColors.primaryLight))
            else
              Column(
                children: faq.map((item) {
                  return Container(
                    margin: const EdgeInsets.only(bottom: 10),
                    decoration: BoxDecoration(
                      color: AppColors.surface,
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: AppColors.surfaceLight),
                    ),
                    child: Theme(
                      data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
                      child: ExpansionTile(
                        iconColor: AppColors.primaryLight,
                        collapsedIconColor: AppColors.textMuted,
                        tilePadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                        title: Text(
                          item['question'] ?? '',
                          style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                        ),
                        children: [
                          Padding(
                            padding: const EdgeInsets.fromLTRB(16, 0, 16, 14),
                            child: Text(
                              item['answer'] ?? '',
                              style: const TextStyle(fontSize: 12, color: AppColors.textSecondary, height: 1.4),
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                }).toList(),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildContactAction({
    required IconData icon,
    required Color color,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: color.withOpacity(0.15),
              borderRadius: BorderRadius.circular(14),
            ),
            child: Icon(icon, color: color, size: 24),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
                const SizedBox(height: 2),
                Text(subtitle, style: const TextStyle(fontSize: 12, color: AppColors.primaryLight, fontWeight: FontWeight.w600)),
              ],
            ),
          ),
          const Icon(Icons.arrow_forward_ios, color: AppColors.textMuted, size: 14),
        ],
      ),
    );
  }
}
