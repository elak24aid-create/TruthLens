import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/history_item.dart';

class LocalHistoryService {
  static const String _storageKey = 'truthlens_local_history_v1';

  /// Fetch cached items from local storage
  Future<List<HistoryItem>> getLocalHistory() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final String? rawJson = prefs.getString(_storageKey);
      if (rawJson == null || rawJson.isEmpty) return [];

      final List<dynamic> decoded = jsonDecode(rawJson);
      return decoded.map((item) => HistoryItem.fromJson(item)).toList();
    } catch (_) {
      return [];
    }
  }

  /// Save single item locally
  Future<void> saveLocalItem(HistoryItem item) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final items = await getLocalHistory();
      items.insert(0, item);
      final encoded = jsonEncode(items.map((i) => i.toJson()).toList());
      await prefs.setString(_storageKey, encoded);
    } catch (_) {}
  }

  /// Remove item by ID
  Future<void> deleteLocalItem(String id) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final items = await getLocalHistory();
      items.removeWhere((i) => i.id == id);
      final encoded = jsonEncode(items.map((i) => i.toJson()).toList());
      await prefs.setString(_storageKey, encoded);
    } catch (_) {}
  }

  /// Clear all local history
  Future<void> clearLocalHistory() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_storageKey);
    } catch (_) {}
  }
}
