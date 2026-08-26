import 'package:flutter/material.dart';
import '../../constants/app_colors.dart';
import '../../services/api_service.dart';

class CashbackScreen extends StatefulWidget {
  const CashbackScreen({super.key});

  @override
  State<CashbackScreen> createState() => _CashbackScreenState();
}

class _CashbackScreenState extends State<CashbackScreen> {
  double _balance = 0.0;
  double _totalEarned = 0.0;
  double _totalSpent = 0.0;
  List<dynamic> _transactions = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadCashback();
  }

  Future<void> _loadCashback() async {
    setState(() => _isLoading = true);
    final data = await ApiService.getCashback();
    setState(() {
      _balance = (data['balance'] as num?)?.toDouble() ?? 0.0;
      _totalEarned = (data['total_earned'] as num?)?.toDouble() ?? 0.0;
      _totalSpent = (data['total_spent'] as num?)?.toDouble() ?? 0.0;
      _transactions = (data['transactions'] as List?) ?? [];
      _isLoading = false;
    });
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
          'Keshbek va Rag\'batlantirish',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: c.textPrimary),
        ),
      ),
      body: RefreshIndicator(
        onRefresh: _loadCashback,
        color: AppColors.primaryLight,
        backgroundColor: c.surface,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Main Gold Card
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  gradient: AppColors.goldGradient,
                  borderRadius: BorderRadius.circular(24),
                  boxShadow: [
                    BoxShadow(
                      color: AppColors.warnYellow.withOpacity(0.3),
                      blurRadius: 20,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: const [
                        Text(
                          'SESPORT BALLARI',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w900,
                            letterSpacing: 2,
                            color: Colors.white70,
                          ),
                        ),
                        Icon(Icons.stars_rounded, color: Colors.white, size: 28),
                      ],
                    ),
                    const SizedBox(height: 16),
                    Text(
                      '${_balance.toStringAsFixed(0)} so\'m',
                      style: const TextStyle(
                        fontSize: 32,
                        fontWeight: FontWeight.w900,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        _buildCardSub(label: 'Jami to\'plangan', val: '+${_totalEarned.toStringAsFixed(0)}'),
                        const SizedBox(width: 24),
                        _buildCardSub(label: 'Ishlatilgan', val: '-${_totalSpent.toStringAsFixed(0)}'),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 28),

              // Info Box
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: c.surface,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: c.surfaceLight),
                  boxShadow: c.cardShadow,
                ),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: AppColors.primary.withOpacity(0.12),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Icon(Icons.info_outline, color: AppColors.primaryLight, size: 22),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Har bir tasdiqlangan va o\'rinli shikoyatingiz uchun rag\'batlantiruvchi keshbek ballari beriladi.',
                        style: TextStyle(fontSize: 12, color: c.textSecondary, height: 1.3),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 28),

              // Transactions Title
              Text(
                'Ballar tarixi',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: c.textPrimary),
              ),
              const SizedBox(height: 12),

              // Transactions List
              if (_isLoading)
                const Center(child: CircularProgressIndicator(color: AppColors.primaryLight))
              else if (_transactions.isEmpty)
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(24),
                  decoration: BoxDecoration(
                    color: c.surface,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: c.surfaceLight),
                  ),
                  child: Center(
                    child: Text(
                      'Hozircha tranzaksiyalar mavjud emas.',
                      style: TextStyle(color: c.textMuted, fontSize: 13),
                    ),
                  ),
                )
              else
                ListView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: _transactions.length,
                  itemBuilder: (context, index) {
                    final tx = _transactions[index];
                    final isEarned = tx['type'] == 'EARNED';

                    return Container(
                      margin: const EdgeInsets.only(bottom: 10),
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: c.surface,
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: c.surfaceLight),
                        boxShadow: c.cardShadow,
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                tx['description'] ?? '',
                                style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: c.textPrimary),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                tx['created_at'] ?? '',
                                style: TextStyle(fontSize: 11, color: c.textMuted),
                              ),
                            ],
                          ),
                          Text(
                            isEarned ? '+${tx['amount']}' : '-${tx['amount']}',
                            style: TextStyle(
                              fontSize: 15,
                              fontWeight: FontWeight.bold,
                              color: isEarned ? AppColors.safeGreen : AppColors.dangerRed,
                            ),
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

  Widget _buildCardSub({required String label, required String val}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(fontSize: 10, color: Colors.white70)),
        const SizedBox(height: 2),
        Text(val, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Colors.white)),
      ],
    );
  }
}
