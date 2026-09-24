import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/history_item.dart';
import '../models/news_article.dart';
import '../models/community_report.dart';

class StorageService {
  static const String _historyKey = 'truthlens_history';
  static const String _newsKey = 'truthlens_news_cache';
  static const String _newsTimeKey = 'truthlens_news_time';
  static const String _reportsKey = 'truthlens_cached_reports';
  static const String _userKey = 'truthlens_user_session';

  // --- HISTORY ---
  static Future<List<HistoryItem>> getHistory() async {
    final prefs = await SharedPreferences.getInstance();
    final jsonList = prefs.getStringList(_historyKey) ?? [];
    return jsonList.map((j) => HistoryItem.fromJson(jsonDecode(j))).toList();
  }

  static Future<void> saveHistoryItem(HistoryItem item) async {
    final prefs = await SharedPreferences.getInstance();
    final items = await getHistory();
    items.insert(0, item);
    final jsonList = items.map((i) => jsonEncode(i.toJson())).toList();
    await prefs.setStringList(_historyKey, jsonList);
  }

  static Future<void> deleteHistoryItem(String id) async {
    final prefs = await SharedPreferences.getInstance();
    final items = await getHistory();
    items.removeWhere((item) => item.id == id);
    final jsonList = items.map((i) => jsonEncode(i.toJson())).toList();
    await prefs.setStringList(_historyKey, jsonList);
  }

  static Future<void> clearHistory() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_historyKey);
  }

  // --- NEWS CACHE ---
  static Future<void> cacheNews(NewsResponse response) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_newsKey, jsonEncode(response.toJson()));
    await prefs.setString(_newsTimeKey, DateTime.now().toIso8601String());
  }

  static Future<Map<String, dynamic>?> getCachedNews() async {
    final prefs = await SharedPreferences.getInstance();
    final newsStr = prefs.getString(_newsKey);
    final timeStr = prefs.getString(_newsTimeKey);
    if (newsStr != null && timeStr != null) {
      return {
        'news': NewsResponse.fromJson(jsonDecode(newsStr)),
        'timestamp': DateTime.parse(timeStr),
      };
    }
    return null;
  }

  // --- AUTH ---
  static Future<void> saveUser(Map<String, String> user) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_userKey, jsonEncode(user));
  }

  static Future<Map<String, String>?> getUser() async {
    final prefs = await SharedPreferences.getInstance();
    final userStr = prefs.getString(_userKey);
    if (userStr != null) {
      return Map<String, String>.from(jsonDecode(userStr));
    }
    return null;
  }
  
  static Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_userKey);
  }

  // --- REPORTS CACHE ---
  static Future<List<CommunityReport>> getCachedReports() async {
    final prefs = await SharedPreferences.getInstance();
    final jsonList = prefs.getStringList(_reportsKey) ?? [];
    return jsonList.map((j) => CommunityReport.fromJson(jsonDecode(j))).toList();
  }

  static Future<void> cacheReports(List<CommunityReport> reports) async {
    final prefs = await SharedPreferences.getInstance();
    final jsonList = reports.map((r) => jsonEncode(r.toJson())).toList();
    await prefs.setStringList(_reportsKey, jsonList);
  }
}
