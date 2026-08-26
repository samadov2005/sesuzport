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
    final c = context.colors;
    String newStatus = complaint.status == 'PENDING' ? 'UNDER_REVIEW' : 'RESOLVED';
    final commentController = TextEditingController(text: complaint.moderationComment);
    final pointsController = TextEditingController(text: '5000');

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: c.surface,
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
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: c.textPrimary),
                  ),
                  IconButton(
                    icon: Icon(Icons.close, color: c.textMuted),
                    onPressed: () => Navigator.pop(ctx),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Text(
                complaint.description,
                style: TextStyle(fontSize: 13, color: c.textSecondary),
              ),
              const SizedBox(height: 16),

              Text('Yangi holat:', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: c.textPrimary)),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                children: [
                  _buildStatusChoice(setModalState, newStatus, 'UNDER_REVIEW', '🔍 Ko\'rib chiqilmoqda', (val) => newStatus = val, c),
                  _buildStatusChoice(setModalState, newStatus, 'RESOLVED', '🟢 Hal qilindi', (val) => newStatus = val, c),
                  _buildStatusChoice(setModalState, newStatus, 'REJECTED', '🔴 Rad etildi', (val) => newStatus = val, c),
                ],
              ),
              const SizedBox(height: 16),

              if (newStatus == 'RESOLVED') ...[
                Text('Rag\'batlantirish balli (Keshbek):', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: c.textPrimary)),
                const SizedBox(height: 6),
                TextField(
                  controller: pointsController,
                  keyboardType: TextInputType.number,
                  style: TextStyle(color: c.textPrimary),
                  decoration: InputDecoration(
                    hintText: '5000',
                    filled: true,
                    fillColor: c.background,
                    suffixText: 'so\'m',
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: c.surfaceLight)),
                    enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: c.surfaceLight)),
                  ),
                ),
                const SizedBox(height: 16),
              ],

              Text('Inspektor izohi (Foydalanuvchiga ko\'rinadi):', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: c.textPrimary)),
              const SizedBox(height: 6),
              TextField(
                controller: commentController,
                maxLines: 2,
                style: TextStyle(color: c.textPrimary),
                decoration: InputDecoration(
                  hintText: 'Masalan: Joyiga chiqib o\'rganildi, mahsulot savdodan olib tashlandi.',
                  filled: true,
                  fillColor: c.background,
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: c.surfaceLight)),
                  enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: c.surfaceLight)),
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
    AppThemeColors c,
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
      backgroundColor: c.background,
      labelStyle: TextStyle(
        color: isSelected ? Colors.white : c.textSecondary,
        fontSize: 12,
        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final c = context.colors;

    final total = _stats['total_complaints'] ?? 0;
    final pending = _stats['pending'] ?? 0;
    final underReview = _stats['under_review'] ?? 0;
    final resolved = _stats['resolved'] ?? 0;

    return Scaffold(
      backgroundColor: c.background,
      appBar: AppBar(
        backgroundColor: c.surface,
        elevation: 0,
        title: Text(
          'SESPORT — Admin & Moderator Boshqaruvi',
          style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: c.textPrimary),
        ),
      ),
      body: RefreshIndicator(
        onRefresh: _loadData,
        color: AppColors.primaryLight,
        backgroundColor: c.surface,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Metric Cards Row
              Row(
                children: [
                  _buildMetricCard('Jami', '$total', Icons.assignment, AppColors.infoBlue, c),
                  const SizedBox(width: 8),
                  _buildMetricCard('Kutilmoqda', '$pending', Icons.hourglass_top, AppColors.warnYellow, c),
                  const SizedBox(width: 8),
                  _buildMetricCard('Jarayonda', '$underReview', Icons.search, AppColors.purple, c),
                  const SizedBox(width: 8),
                  _buildMetricCard('Hal qilindi', '$resolved', Icons.check_circle, AppColors.safeGreen, c),
                ],
              ),
              const SizedBox(height: 20),

              // Filter Chips
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: [
                    _buildFilterChip(null, 'Barchasi ($total)', c),
                    const SizedBox(width: 8),
                    _buildFilterChip('PENDING', '🟡 Kutilmoqda ($pending)', c),
                    const SizedBox(width: 8),
                    _buildFilterChip('UNDER_REVIEW', '🔍 Jarayonda ($underReview)', c),
                    const SizedBox(width: 8),
                    _buildFilterChip('RESOLVED', '🟢 Hal qilingan ($resolved)', c),
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
                    color: c.surface,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: c.surfaceLight),
                  ),
                  child: Center(
                    child: Text('Ushbu holatda murojaatlar yo\'q.', style: TextStyle(color: c.textMuted)),
                  ),
                )
              else
                ListView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: _complaints.length,
                  itemBuilder: (context, index) {
                    final item = _complaints[index];
                    final statusColor = _getStatusColor(item.status);

                    return Container(
                      margin: const EdgeInsets.only(bottom: 12),
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
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(item.ticketId, style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: c.textPrimary)),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                decoration: BoxDecoration(
                                  color: statusColor.withOpacity(0.15),
                                  borderRadius: BorderRadius.circular(20),
                                  border: Border.all(color: statusColor.withOpacity(0.4)),
                                ),
                                child: Text(item.statusDisplay, style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: statusColor)),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Text(item.description, style: TextStyle(fontSize: 13, color: c.textSecondary, height: 1.3)),
                          const SizedBox(height: 10),

                          if (item.moderationComment.isNotEmpty) ...[
                            Container(
                              padding: const EdgeInsets.all(10),
                              decoration: BoxDecoration(
                                color: c.background,
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: Text('Izoh: ${item.moderationComment}', style: TextStyle(fontSize: 11, color: c.textMuted)),
                            ),
                            const SizedBox(height: 10),
                          ],

                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(item.createdAt, style: TextStyle(fontSize: 11, color: c.textMuted)),
                              ElevatedButton.icon(
                                onPressed: () => _openModerateDialog(item),
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

  Widget _buildMetricCard(String label, String value, IconData icon, Color color, AppThemeColors c) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
        decoration: BoxDecoration(
          color: c.surface,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: c.surfaceLight),
          boxShadow: c.cardShadow,
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 20),
            const SizedBox(height: 4),
            Text(value, style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: c.textPrimary)),
            const SizedBox(height: 2),
            Text(label, maxLines: 1, overflow: TextOverflow.ellipsis, style: TextStyle(fontSize: 9, color: c.textSecondary)),
          ],
        ),
      ),
    );
  }

  Widget _buildFilterChip(String? status, String label, AppThemeColors c) {
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
      backgroundColor: c.surface,
      labelStyle: TextStyle(
        color: isSelected ? Colors.white : c.textSecondary,
        fontSize: 11,
        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
      ),
    );
  }
}
