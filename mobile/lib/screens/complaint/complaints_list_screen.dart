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
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.surface,
        elevation: 0,
        title: const Text(
          'Mening murojaatlarim',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
        ),
      ),
      body: RefreshIndicator(
        onRefresh: _loadComplaints,
        color: AppColors.primaryLight,
        backgroundColor: AppColors.surface,
        child: _isLoading
            ? const Center(child: CircularProgressIndicator(color: AppColors.primaryLight))
            : _complaints.isEmpty
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: const [
                        Icon(Icons.inbox_outlined, size: 64, color: AppColors.textMuted),
                        SizedBox(height: 12),
                        Text(
                          'Hozircha murojaatlar yo\'q',
                          style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: AppColors.textSecondary),
                        ),
                        SizedBox(height: 4),
                        Text(
                          'Sifatsiz mahsulot topsangiz, kamera orqali yuboring.',
                          style: TextStyle(fontSize: 12, color: AppColors.textMuted),
                        ),
                      ],
                    ),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _complaints.length,
                    itemBuilder: (context, index) {
                      final c = _complaints[index];
                      final statusColor = _getStatusColor(c.status);

                      return Container(
                        margin: const EdgeInsets.only(bottom: 14),
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: AppColors.surface,
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(color: AppColors.surfaceLight),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            // Header Row (Ticket ID + Status Chip)
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(
                                  c.ticketId,
                                  style: const TextStyle(
                                    fontSize: 14,
                                    fontWeight: FontWeight.bold,
                                    color: AppColors.textPrimary,
                                  ),
                                ),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                  decoration: BoxDecoration(
                                    color: statusColor.withOpacity(0.2),
                                    borderRadius: BorderRadius.circular(20),
                                    border: Border.all(color: statusColor.withOpacity(0.5)),
                                  ),
                                  child: Text(
                                    c.statusDisplay,
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
                              c.description,
                              style: const TextStyle(fontSize: 13, color: AppColors.textSecondary, height: 1.3),
                            ),
                            const SizedBox(height: 12),

                            // Moderation Comment if exists
                            if (c.moderationComment.isNotEmpty) ...[
                              Container(
                                padding: const EdgeInsets.all(10),
                                decoration: BoxDecoration(
                                  color: AppColors.background,
                                  borderRadius: BorderRadius.circular(10),
                                ),
                                child: Row(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    const Icon(Icons.info_outline, size: 16, color: AppColors.primaryLight),
                                    const SizedBox(width: 8),
                                    Expanded(
                                      child: Text(
                                        'Inspektor xulosasi: ${c.moderationComment}',
                                        style: const TextStyle(fontSize: 11, color: AppColors.textSecondary),
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
                                    const Icon(Icons.access_time, size: 13, color: AppColors.textMuted),
                                    const SizedBox(width: 4),
                                    Text(
                                      c.createdAt,
                                      style: const TextStyle(fontSize: 11, color: AppColors.textMuted),
                                    ),
                                  ],
                                ),
                                Row(
                                  children: [
                                    const Icon(Icons.location_on_outlined, size: 13, color: AppColors.textMuted),
                                    const SizedBox(width: 2),
                                    Text(
                                      '${c.latitude.toStringAsFixed(3)}, ${c.longitude.toStringAsFixed(3)}',
                                      style: const TextStyle(fontSize: 11, color: AppColors.textMuted),
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
