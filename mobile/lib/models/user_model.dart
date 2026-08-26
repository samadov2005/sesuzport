class UserModel {
  final int id;
  final int telegramId;
  final String fullName;
  final String phoneNumber;
  final String language;
  final String role;
  final double cashbackBalance;
  final int totalComplaints;
  final int resolvedComplaints;

  UserModel({
    required this.id,
    required this.telegramId,
    required this.fullName,
    required this.phoneNumber,
    required this.language,
    required this.role,
    this.cashbackBalance = 0.0,
    this.totalComplaints = 0,
    this.resolvedComplaints = 0,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    final stats = json['stats'] as Map<String, dynamic>?;
    return UserModel(
      id: json['id'] ?? 0,
      telegramId: json['telegram_id'] ?? 0,
      fullName: json['full_name'] ?? 'Foydalanuvchi',
      phoneNumber: json['phone_number'] ?? '',
      language: json['language'] ?? 'uz',
      role: json['role'] ?? 'CONSUMER',
      cashbackBalance: (json['cashback_balance'] as num?)?.toDouble() ?? 0.0,
      totalComplaints: stats?['total_complaints'] ?? 0,
      resolvedComplaints: stats?['resolved_complaints'] ?? 0,
    );
  }
}
