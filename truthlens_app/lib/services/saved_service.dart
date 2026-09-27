import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/analysis_result.dart';

class SavedResult {
  final String id;
  final String claim;
  final AnalysisResult result;
  final String date;
  String? note;

  SavedResult({
    required this.id,
    required this.claim,
    required this.result,
    required this.date,
    this.note,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'claim': claim,
      'result': result.toJson(),
      'date': date,
      'note': note,
    };
  }

  factory SavedResult.fromJson(Map<String, dynamic> json) {
    return SavedResult(
      id: json['id'],
      claim: json['claim'],
      result: AnalysisResult.fromJson(json['result']),
      date: json['date'],
      note: json['note'],
    );
  }
}

class SavedService {
  static const String _key = 'saved_results_key';

  Future<void> saveResult(SavedResult result) async {
    final prefs = await SharedPreferences.getInstance();
    List<String> items = prefs.getStringList(_key) ?? [];
    
    int index = items.indexWhere((element) {
      final jsonMap = jsonDecode(element);
      return jsonMap['id'] == result.id;
    });

    if (index != -1) {
      items[index] = jsonEncode(result.toJson());
    } else {
      items.add(jsonEncode(result.toJson()));
    }
    await prefs.setStringList(_key, items);
  }

  Future<List<SavedResult>> getSavedResults() async {
    final prefs = await SharedPreferences.getInstance();
    List<String> items = prefs.getStringList(_key) ?? [];
    return items.map((e) => SavedResult.fromJson(jsonDecode(e))).toList();
  }

  Future<void> clearSaved() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_key);
  }
}
