import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import 'package:truthlens_app/config/api_config.dart';
import 'package:truthlens_app/services/storage_service.dart';

class AuthService {
  static String get baseUrl => '${ApiConfig.baseUrl}/auth';
  static const String tokenKey = 'truthlens_token';
  static const String emailKey = 'truthlens_email';

  static Future<void> setToken(String token, String email) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(tokenKey, token);
    await prefs.setString(emailKey, email);
  }

  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(tokenKey);
  }

  static Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString(tokenKey);
    if (token != null) {
      try {
        await http.post(
          Uri.parse('$baseUrl/logout'),
          headers: {'Authorization': 'Bearer $token'},
        );
      } catch (e) {
        // ignore
      }
    }
    await prefs.remove(tokenKey);
    await prefs.remove(emailKey);
    await StorageService.logout();
  }

  static Future<bool> fetchUser(String token) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/me'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        await StorageService.saveUser({'email': data['email'], 'name': data['name'] ?? data['email'].split('@')[0]});
        return true;
      }
      return false;
    } catch (_) {
      return false;
    }
  }

  static Future<bool> login(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'password': password}),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        await setToken(data['token'], data['email']);
        await StorageService.saveUser({'email': data['email'], 'name': data['name'] ?? data['email'].split('@')[0]});
        return true;
      } else if (response.statusCode == 401) {
        throw Exception('Invalid credentials');
      } else if (response.statusCode == 422) {
        throw Exception('Invalid input format');
      }
      throw Exception('Server error: ${response.statusCode}');
    } catch (e) {
      if (e is Exception && e.toString().startsWith('Exception:')) {
        rethrow;
      }
      throw Exception('Network error or server unavailable');
    }
  }

  static Future<bool> register(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/register'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'password': password}),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        await setToken(data['token'], data['email']);
        await StorageService.saveUser({'email': data['email'], 'name': data['name'] ?? data['email'].split('@')[0]});
        return true;
      } else if (response.statusCode == 400) {
        throw Exception('Email already registered');
      } else if (response.statusCode == 422) {
        throw Exception('Invalid input format');
      }
      throw Exception('Server error: ${response.statusCode}');
    } catch (e) {
      if (e is Exception && e.toString().startsWith('Exception:')) {
        rethrow;
      }
      throw Exception('Network error or server unavailable');
    }
  }
}
