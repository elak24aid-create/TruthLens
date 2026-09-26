import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class AuthService {
  static const String baseUrl = 'http://127.0.0.1:8000/api/auth';
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
        return true;
      }
      return false;
    } catch (e) {
      return false;
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
        return true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }
}
