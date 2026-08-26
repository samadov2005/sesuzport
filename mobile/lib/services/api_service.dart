import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../constants/api_constants.dart';
import '../models/user_model.dart';
import '../models/complaint_model.dart';
import '../models/store_model.dart';

class ApiService {
  static const String _tokenKey = 'sesport_auth_token';

  // ── Auth & Token ───────────────────────────────────────────
  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }

  static Future<void> saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
  }

  static Future<void> clearToken() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
  }

  static Map<String, String> _headers(String? token) {
    final map = {'Content-Type': 'application/json'};
    if (token != null && token.isNotEmpty) {
      map['Authorization'] = 'Bearer $token';
    }
    return map;
  }

  // ── Login / Register ───────────────────────────────────────
  static Future<Map<String, dynamic>> login({
    required String phoneNumber,
    required String fullName,
    String language = 'uz',
  }) async {
    try {
      final response = await http.post(
        Uri.parse(ApiConstants.login),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'phone_number': phoneNumber,
          'full_name': fullName,
          'language': language,
        }),
      );

      final data = jsonDecode(utf8.decode(response.bodyBytes));
      if (response.statusCode == 200 && data['success'] == true) {
        final token = data['token'] as String;
        await saveToken(token);
        return {'success': true, 'user': UserModel.fromJson(data['user'])};
      } else {
        return {'success': false, 'error': data['error'] ?? 'Kirishda xatolik yuz berdi.'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Tarmoqqa ulanishda xatolik: $e'};
    }
  }

  // ── User Profile ───────────────────────────────────────────
  static Future<UserModel?> getProfile() async {
    try {
      final token = await getToken();
      if (token == null) return null;

      final response = await http.get(
        Uri.parse(ApiConstants.profile),
        headers: _headers(token),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        if (data['success'] == true) {
          return UserModel.fromJson(data['user']);
        }
      }
      return null;
    } catch (_) {
      return null;
    }
  }

  // ── Complaints ─────────────────────────────────────────────
  static Future<Map<String, dynamic>> submitComplaint({
    required String description,
    required String imageBase64,
    required double latitude,
    required double longitude,
  }) async {
    try {
      final token = await getToken();
      final response = await http.post(
        Uri.parse(ApiConstants.createComplaint),
        headers: _headers(token),
        body: jsonEncode({
          'description': description,
          'image': imageBase64,
          'latitude': latitude,
          'longitude': longitude,
        }),
      );

      final data = jsonDecode(utf8.decode(response.bodyBytes));
      return data;
    } catch (e) {
      return {'success': false, 'error': 'Yuborishda xatolik: $e'};
    }
  }

  static Future<List<ComplaintModel>> getMyComplaints() async {
    try {
      final token = await getToken();
      final response = await http.get(
        Uri.parse(ApiConstants.myComplaints),
        headers: _headers(token),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        if (data['success'] == true && data['complaints'] != null) {
          return (data['complaints'] as List)
              .map((c) => ComplaintModel.fromJson(c))
              .toList();
        }
      }
      return [];
    } catch (_) {
      return [];
    }
  }

  // ── Stores ─────────────────────────────────────────────────
  static Future<List<StoreModel>> getStores({
    String? status,
    String? query,
    double? lat,
    double? lng,
  }) async {
    try {
      final queryParams = <String, String>{};
      if (status != null && status.isNotEmpty) queryParams['status'] = status;
      if (query != null && query.isNotEmpty) queryParams['q'] = query;
      if (lat != null && lng != null) {
        queryParams['lat'] = lat.toString();
        queryParams['lng'] = lng.toString();
      }

      final uri = Uri.parse(ApiConstants.stores).replace(queryParameters: queryParams);
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        if (data['success'] == true && data['stores'] != null) {
          return (data['stores'] as List)
              .map((s) => StoreModel.fromJson(s))
              .toList();
        }
      }
      return [];
    } catch (_) {
      return [];
    }
  }

  // ── Cashback ───────────────────────────────────────────────
  static Future<Map<String, dynamic>> getCashback() async {
    try {
      final token = await getToken();
      final response = await http.get(
        Uri.parse(ApiConstants.cashback),
        headers: _headers(token),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        if (data['success'] == true) {
          return data;
        }
      }
      return {'balance': 0.0, 'total_earned': 0.0, 'total_spent': 0.0, 'transactions': []};
    } catch (_) {
      return {'balance': 0.0, 'total_earned': 0.0, 'total_spent': 0.0, 'transactions': []};
    }
  }

  // ── Rights & Support ───────────────────────────────────────
  static Future<List<Map<String, dynamic>>> getRights() async {
    try {
      final response = await http.get(Uri.parse(ApiConstants.rights));
      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        if (data['success'] == true && data['rights'] != null) {
          return List<Map<String, dynamic>>.from(data['rights']);
        }
      }
      return [];
    } catch (_) {
      return [];
    }
  }

  static Future<Map<String, dynamic>> getSupportInfo() async {
    try {
      final response = await http.get(Uri.parse(ApiConstants.support));
      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        if (data['success'] == true && data['support'] != null) {
          return Map<String, dynamic>.from(data['support']);
        }
      }
      return {};
    } catch (_) {
      return {};
    }
  }

  // ── Admin & Moderation ─────────────────────────────────────
  static Future<Map<String, dynamic>> getAdminStats() async {
    try {
      final token = await getToken();
      final response = await http.get(
        Uri.parse(ApiConstants.adminStats),
        headers: _headers(token),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        if (data['success'] == true) {
          return Map<String, dynamic>.from(data['stats']);
        }
      }
      return {};
    } catch (_) {
      return {};
    }
  }

  static Future<List<ComplaintModel>> getAdminComplaints({String? status}) async {
    try {
      final token = await getToken();
      final queryParams = <String, String>{};
      if (status != null && status.isNotEmpty) queryParams['status'] = status;

      final uri = Uri.parse(ApiConstants.adminComplaints).replace(queryParameters: queryParams);
      final response = await http.get(uri, headers: _headers(token));

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        if (data['success'] == true && data['complaints'] != null) {
          return (data['complaints'] as List)
              .map((c) => ComplaintModel.fromJson(c))
              .toList();
        }
      }
      return [];
    } catch (_) {
      return [];
    }
  }

  static Future<Map<String, dynamic>> moderateComplaint({
    required int complaintId,
    required String status,
    String? comment,
    int? points,
  }) async {
    try {
      final token = await getToken();
      final response = await http.post(
        Uri.parse(ApiConstants.adminModerate(complaintId)),
        headers: _headers(token),
        body: jsonEncode({
          'status': status,
          'moderation_comment': comment ?? '',
          'points': points ?? 0,
        }),
      );
      final data = jsonDecode(utf8.decode(response.bodyBytes));
      return data;
    } catch (e) {
      return {'success': false, 'error': 'Moderatsiyada xatolik: $e'};
    }
  }
}
