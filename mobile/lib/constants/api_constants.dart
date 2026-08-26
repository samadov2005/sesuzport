class ApiConstants {
  // Production URL on Render
  static const String baseUrl = 'https://sesuzport.onrender.com/api/v1';

  // Auth & Profile
  static const String login = '$baseUrl/auth/login/';
  static const String register = '$baseUrl/auth/register/';
  static const String profile = '$baseUrl/user/profile/';

  // Complaints
  static const String createComplaint = '$baseUrl/complaints/create/';
  static const String myComplaints = '$baseUrl/complaints/my/';
  static String complaintDetail(String ticketId) => '$baseUrl/complaints/$ticketId/';

  // Stores
  static const String stores = '$baseUrl/stores/';

  // Cashback
  static const String cashback = '$baseUrl/cashback/';

  // Rights & Support
  static const String rights = '$baseUrl/rights/';
  static const String support = '$baseUrl/support/';

  // Admin & Moderation
  static const String adminStats = '$baseUrl/admin/stats/';
  static const String adminComplaints = '$baseUrl/admin/complaints/';
  static String adminModerate(int id) => '$baseUrl/admin/complaints/$id/moderate/';
}
