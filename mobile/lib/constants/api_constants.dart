class ApiConstants {
  // Production Render Backend URL (Official SESPORT domain)
  static const String baseUrl = 'https://sesuzport.onrender.com/api/v1';

  // Auth & User
  static const String login = '$baseUrl/auth/login/';
  static const String profile = '$baseUrl/user/profile/';

  // Complaints
  static const String createComplaint = '$baseUrl/complaints/create/';
  static const String myComplaints = '$baseUrl/complaints/my/';
  static String complaintDetail(String ticketId) => '$baseUrl/complaints/$ticketId/';

  // Stores & Map
  static const String stores = '$baseUrl/stores/';

  // Cashback
  static const String cashback = '$baseUrl/cashback/';

  // Rights & Support
  static const String rights = '$baseUrl/rights/';
  static const String support = '$baseUrl/support/';

  // Hotline & Telegram Handles
  static const String hotline = '1080';
  static const String adminTelegram = 'sesport_admin';
  static const String developerTelegram = 'samadov2005';
}
