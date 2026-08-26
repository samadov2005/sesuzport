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

  // ── Profile ────────────────────────────────────────────────
  static Future<UserModel?> getProfile() async {
    final token = await getToken();
    if (token == null) return null;

    try {
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
    } catch (_) {}
    return null;
  }

  // ── Complaints ─────────────────────────────────────────────
  static Future<Map<String, dynamic>> submitComplaint({
    required String description,
    required String imageBase64,
    required double latitude,
    required double longitude,
  }) async {
    final token = await getToken();
    try {
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
      if (response.statusCode == 200 && data['success'] == true) {
        return {
          'success': true,
          'ticket_id': data['ticket_id'],
          'message': data['message'],
        };
      } else {
        return {'success': false, 'error': data['error'] ?? 'Xatolik yuz berdi.'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Murojaat yuborishda xatolik: $e'};
    }
  }

  static Future<List<ComplaintModel>> getMyComplaints() async {
    final token = await getToken();
    try {
      final response = await http.get(
        Uri.parse(ApiConstants.myComplaints),
        headers: _headers(token),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        if (data['success'] == true) {
          final list = data['complaints'] as List;
          return list.map((e) => ComplaintModel.fromJson(e)).toList();
        }
      }
    } catch (_) {}
    return [];
  }

  // ── Stores ─────────────────────────────────────────────────
  static Future<List<StoreModel>> getStores({
    String? status,
    String? query,
    double? lat,
    double? lon,
  }) async {
    try {
      final params = <String, String>{};
      if (status != null) params['status'] = status;
      if (query != null && query.isNotEmpty) params['q'] = query;
      if (lat != null && lon != null) {
        params['lat'] = lat.toString();
        params['lon'] = lon.toString();
      }

      final uri = Uri.parse(ApiConstants.stores).replace(queryParameters: params);
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        if (data['success'] == true) {
          final list = data['stores'] as List;
          return list.map((e) => StoreModel.fromJson(e)).toList();
        }
      }
    } catch (_) {}
    return [];
  }

  // ── Cashback ───────────────────────────────────────────────
  static Future<Map<String, dynamic>> getCashback() async {
    final token = await getToken();
    try {
      final response = await http.get(
        Uri.parse(ApiConstants.cashback),
        headers: _headers(token),
      );
      if (response.statusCode == 200) {
        return jsonDecode(utf8.decode(response.bodyBytes));
      }
    } catch (_) {}
    return {'success': false, 'balance': 0.0, 'transactions': []};
  }

  // ── Rights & Support ───────────────────────────────────────
  static Future<List<Map<String, dynamic>>> getRights() async {
    try {
      final response = await http.get(Uri.parse(ApiConstants.rights));
      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        if (data['success'] == true) {
          return List<Map<String, dynamic>>.from(data['rights']);
        }
      }
    } catch (_) {}
    return [];
  }

  static Future<Map<String, dynamic>> getSupportInfo() async {
    try {
      final response = await http.get(Uri.parse(ApiConstants.support));
      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        return data['support'] ?? {};
      }
    } catch (_) {}
    return {};
  }
}
