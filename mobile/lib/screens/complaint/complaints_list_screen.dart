import 'package:flutter/material.dart';
import '../../constants/app_colors.dart';
import '../../models/complaint_model.dart';
import '../../services/api_service.dart';

class ComplaintsListScreen extends StatefulWidget {
  const ComplaintsListScreen({super.key});

  @override
  State<ComplaintsListScreen> createState() => _ComplaintsListScreenState();
}

class _ComplaintsListScreenState extends State<ComplaintsListScreen> {
  List<ComplaintModel> _complaints = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadComplaints();
  }

  Future<void> _loadComplaints() async {
    setState(() => _isLoading = true);
    final list = await ApiService.getMyComplaints();
    setState(() {
      _complaints = list;
      _isLoading = false;
    });
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'RESOLVED':
        return AppColors.safeGreen;
      case 'APPROVED':
      case 'UNDER_REVIEW':
        return AppColors.infoBlue;
      case 'REJECTED':
        return AppColors.dangerRed;
      case 'PENDING':
      default:
        return AppColors.warnYellow;
    }
  }

  @override
  Widget build(BuildContext context) {
    final c = context.colors;

    return Scaffold(
      backgroundColor: c.background,
      appBar: AppBar(
        backgroundColor: c.surface,
        elevation: 0,
        title: Text(
          'Mening murojaatlarim',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: c.textPrimary),
        ),
      ),
      body: RefreshIndicator(
        onRefresh: _loadComplaints,
        color: AppColors.primaryLight,
        backgroundColor: c.surface,
        child: _isLoading
            ? const Center(child: CircularProgressIndicator(color: AppColors.primaryLight))
            : _complaints.isEmpty
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.inbox_outlined, size: 64, color: c.textMuted),
                        const SizedBox(height: 12),
                        Text(
                          'Hozircha murojaatlar yo\'q',
                          style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: c.textSecondary),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Sifatsiz mahsulot topsangiz, kamera orqali yuboring.',
                          style: TextStyle(fontSize: 12, color: c.textMuted),
                        ),
                      ],
                    ),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _complaints.length,
                    itemBuilder: (context, index) {
                      final item = _complaints[index];
                      final statusColor = _getStatusColor(item.status);

                      return Container(
                        margin: const EdgeInsets.only(bottom: 14),
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: c.surface,
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(color: c.surfaceLight),
                          boxShadow: c.cardShadow,
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            // Header Row (Ticket ID + Status Chip)
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(
                                  item.ticketId,
                                  style: TextStyle(
                                    fontSize: 14,
                                    fontWeight: FontWeight.bold,
                                    color: c.textPrimary,
                                  ),
                                ),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                  decoration: BoxDecoration(
                                    color: statusColor.withOpacity(0.15),
                                    borderRadius: BorderRadius.circular(20),
                                    border: Border.all(color: statusColor.withOpacity(0.4)),
                                  ),
                                  child: Text(
                                    item.statusDisplay,
                                    style: TextStyle(
                                      fontSize: 11,
                                      fontWeight: FontWeight.bold,
                                      color: statusColor,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 10),

                            // Description
                            Text(
                              item.description,
                              style: TextStyle(fontSize: 13, color: c.textSecondary, height: 1.3),
                            ),
                            const SizedBox(height: 12),

                            // Moderation Comment if exists
                            if (item.moderationComment.isNotEmpty) ...[
                              Container(
                                padding: const EdgeInsets.all(10),
                                decoration: BoxDecoration(
                                  color: c.background,
                                  borderRadius: BorderRadius.circular(10),
                                ),
                                child: Row(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    const Icon(Icons.info_outline, size: 16, color: AppColors.primaryLight),
                                    const SizedBox(width: 8),
                                    Expanded(
                                      child: Text(
                                        'Inspektor xulosasi: ${item.moderationComment}',
                                        style: TextStyle(fontSize: 11, color: c.textSecondary),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              const SizedBox(height: 10),
                            ],

                            // Date & GPS Footer
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Row(
                                  children: [
                                    Icon(Icons.access_time, size: 13, color: c.textMuted),
                                    const SizedBox(width: 4),
                                    Text(
                                      item.createdAt,
                                      style: TextStyle(fontSize: 11, color: c.textMuted),
                                    ),
                                  ],
                                ),
                                Row(
                                  children: [
                                    Icon(Icons.location_on_outlined, size: 13, color: c.textMuted),
                                    const SizedBox(width: 2),
                                    Text(
                                      '${item.latitude.toStringAsFixed(3)}, ${item.longitude.toStringAsFixed(3)}',
                                      style: TextStyle(fontSize: 11, color: c.textMuted),
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ],
                        ),
                      );
                    },
                  ),
      ),
    );
  }
}
