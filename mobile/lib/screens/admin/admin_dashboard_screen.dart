import 'package:flutter/material.dart';
import '../../constants/app_colors.dart';
import '../../models/complaint_model.dart';
import '../../services/api_service.dart';

class AdminDashboardScreen extends StatefulWidget {
  const AdminDashboardScreen({super.key});

  @override
  State<AdminDashboardScreen> createState() => _AdminDashboardScreenState();
}

class _AdminDashboardScreenState extends State<AdminDashboardScreen> {
  Map<String, dynamic> _stats = {};
  List<ComplaintModel> _complaints = [];
  String? _selectedStatus;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    final stats = await ApiService.getAdminStats();
    final list = await ApiService.getAdminComplaints(status: _selectedStatus);
    setState(() {
      _stats = stats;
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

  void _openModerateDialog(ComplaintModel complaint) {
    String newStatus = complaint.status == 'PENDING' ? 'UNDER_REVIEW' : 'RESOLVED';
    final commentController = TextEditingController(text: complaint.moderationComment);
    final pointsController = TextEditingController(text: '5000');

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: AppColors.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) => StatefulBuilder(
        builder: (context, setModalState) => Padding(
          padding: EdgeInsets.only(
            left: 20,
            right: 20,
            top: 20,
            bottom: MediaQuery.of(context).viewInsets.bottom + 24,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Murojaatni tekshirish #${complaint.ticketId}',
                    style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, color: AppColors.textMuted),
                    onPressed: () => Navigator.pop(ctx),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Text(
                complaint.description,
                style: const TextStyle(fontSize: 13, color: AppColors.textSecondary),
              ),
              const SizedBox(height: 16),

              const Text('Yangi holat:', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                children: [
                  _buildStatusChoice(setModalState, newStatus, 'UNDER_REVIEW', '🔍 Ko\'rib chiqilmoqda', (val) => newStatus = val),
                  _buildStatusChoice(setModalState, newStatus, 'RESOLVED', '🟢 Hal qilindi', (val) => newStatus = val),
                  _buildStatusChoice(setModalState, newStatus, 'REJECTED', '🔴 Rad etildi', (val) => newStatus = val),
                ],
              ),
              const SizedBox(height: 16),

              if (newStatus == 'RESOLVED') ...[
                const Text('Rag\'batlantirish balli (Keshbek):', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
                const SizedBox(height: 6),
                TextField(
                  controller: pointsController,
                  keyboardType: TextInputType.number,
                  style: const TextStyle(color: AppColors.textPrimary),
                  decoration: InputDecoration(
                    hintText: '5000',
                    filled: true,
                    fillColor: AppColors.background,
                    suffixText: 'so\'m',
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
                  ),
                ),
                const SizedBox(height: 16),
              ],

              const Text('Inspektor izohi (Foydalanuvchiga ko\'rinadi):', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
              const SizedBox(height: 6),
              TextField(
                controller: commentController,
                maxLines: 2,
                style: const TextStyle(color: AppColors.textPrimary),
                decoration: InputDecoration(
                  hintText: 'Masalan: Joyiga chiqib o\'rganildi, mahsulot savdodan olib tashlandi.',
                  filled: true,
                  fillColor: AppColors.background,
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
                ),
              ),
              const SizedBox(height: 20),

              SizedBox(
                width: double.infinity,
                height: 48,
                child: ElevatedButton(
                  onPressed: () async {
                    final points = int.tryParse(pointsController.text.trim()) ?? 0;
                    Navigator.pop(ctx);

                    final res = await ApiService.moderateComplaint(
                      complaintId: complaint.id,
                      status: newStatus,
                      comment: commentController.text.trim(),
                      points: points,
                    );

                    if (res['success'] == true) {
                      _loadData();
                      if (mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text(res['message'] ?? 'Yangilandi!'), backgroundColor: AppColors.safeGreen),
                        );
                      }
                    }
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  child: const Text('Saqlash va Tasdiqlash', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatusChoice(
    StateSetter setModalState,
    String current,
    String target,
    String label,
    Function(String) onSelect,
  ) {
    final isSelected = current == target;
    return ChoiceChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (selected) {
        if (selected) {
          setModalState(() => onSelect(target));
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

  @override
  Widget build(BuildContext context) {
    final total = _stats['total_complaints'] ?? 0;
    final pending = _stats['pending'] ?? 0;
    final underReview = _stats['under_review'] ?? 0;
    final resolved = _stats['resolved'] ?? 0;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.surface,
        elevation: 0,
        title: const Text(
          'SESPORT — Admin & Moderator Boshqaruvi',
          style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
        ),
      ),
      body: RefreshIndicator(
        onRefresh: _loadData,
        color: AppColors.primaryLight,
        backgroundColor: AppColors.surface,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Metric Cards Row
              Row(
                children: [
                  _buildMetricCard('Jami', '$total', Icons.assignment, AppColors.infoBlue),
                  const SizedBox(width: 8),
                  _buildMetricCard('Kutilmoqda', '$pending', Icons.hourglass_top, AppColors.warnYellow),
                  const SizedBox(width: 8),
                  _buildMetricCard('Jarayonda', '$underReview', Icons.search, AppColors.purple),
                  const SizedBox(width: 8),
                  _buildMetricCard('Hal qilindi', '$resolved', Icons.check_circle, AppColors.safeGreen),
                ],
              ),
              const SizedBox(height: 20),

              // Filter Chips
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: [
                    _buildFilterChip(null, 'Barchasi ($total)'),
                    const SizedBox(width: 8),
                    _buildFilterChip('PENDING', '🟡 Kutilmoqda ($pending)'),
                    const SizedBox(width: 8),
                    _buildFilterChip('UNDER_REVIEW', '🔍 Jarayonda ($underReview)'),
                    const SizedBox(width: 8),
                    _buildFilterChip('RESOLVED', '🟢 Hal qilingan ($resolved)'),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // Complaints List
              if (_isLoading)
                const Center(child: Padding(padding: EdgeInsets.all(32), child: CircularProgressIndicator(color: AppColors.primaryLight)))
              else if (_complaints.isEmpty)
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(32),
                  decoration: BoxDecoration(
                    color: AppColors.surface,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: const Center(
                    child: Text('Ushbu holatda murojaatlar yo\'q.', style: TextStyle(color: AppColors.textMuted)),
                  ),
                )
              else
                ListView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: _complaints.length,
                  itemBuilder: (context, index) {
                    final c = _complaints[index];
                    final statusColor = _getStatusColor(c.status);

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
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(c.ticketId, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                decoration: BoxDecoration(
                                  color: statusColor.withOpacity(0.2),
                                  borderRadius: BorderRadius.circular(20),
                                  border: Border.all(color: statusColor.withOpacity(0.5)),
                                ),
                                child: Text(c.statusDisplay, style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: statusColor)),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Text(c.description, style: const TextStyle(fontSize: 13, color: AppColors.textSecondary, height: 1.3)),
                          const SizedBox(height: 10),

                          if (c.moderationComment.isNotEmpty) ...[
                            Container(
                              padding: const EdgeInsets.all(10),
                              decoration: BoxDecoration(
                                color: AppColors.background,
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: Text('Izoh: ${c.moderationComment}', style: const TextStyle(fontSize: 11, color: AppColors.textMuted)),
                            ),
                            const SizedBox(height: 10),
                          ],

                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(c.createdAt, style: const TextStyle(fontSize: 11, color: AppColors.textMuted)),
                              ElevatedButton.icon(
                                onPressed: () => _openModerateDialog(c),
                                icon: const Icon(Icons.edit_note_rounded, size: 16, color: Colors.white),
                                label: const Text('Ko\'rib chiqish', style: TextStyle(fontSize: 12, color: Colors.white, fontWeight: FontWeight.bold)),
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: AppColors.primary,
                                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    );
                  },
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMetricCard(String label, String value, IconData icon, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: AppColors.surfaceLight),
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 20),
            const SizedBox(height: 4),
            Text(value, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
            const SizedBox(height: 2),
            Text(label, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 9, color: AppColors.textSecondary)),
          ],
        ),
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
          _loadData();
        }
      },
      selectedColor: AppColors.primary,
      backgroundColor: AppColors.surface,
      labelStyle: TextStyle(
        color: isSelected ? Colors.white : AppColors.textSecondary,
        fontSize: 11,
        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
      ),
    );
  }
}
