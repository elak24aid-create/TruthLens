import 'dart:convert';
import 'dart:io';
import 'dart:async';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import '../config/api_config.dart';
import '../models/analysis_result.dart';
import '../models/history_item.dart';
import '../models/research_result.dart';
import '../models/news_article.dart';
import '../models/community_report.dart';
import '../models/verdict.dart';
import 'storage_service.dart';

class ApiException implements Exception {
  final String message;
  final int? statusCode;
  ApiException(this.message, [this.statusCode]);
  @override
  String toString() => message;
}

class ApiService {
  final http.Client _client;

  ApiService({http.Client? client}) : _client = client ?? http.Client();

  Future<bool> checkHealth() async {
    try {
      final response = await _client.get(Uri.parse(ApiConfig.healthEndpoint)).timeout(ApiConfig.requestTimeout);
      if (response.statusCode == 200) {
        return jsonDecode(response.body)['status'] == 'ok';
      }
      return false;
    } catch (_) {
      return false;
    }
  }

  Future<AnalysisResult> checkText(String text) async {
    try {
      final response = await _client.post(
        Uri.parse(ApiConfig.checkTextEndpoint),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'text': text}),
      ).timeout(ApiConfig.requestTimeout);
      if (response.statusCode == 200) return AnalysisResult.fromJson(jsonDecode(response.body));
      
      String errorMsg = 'Failed to analyze text (Status ${response.statusCode})';
      try {
        final decoded = jsonDecode(response.body);
        if (decoded['detail'] != null) errorMsg = decoded['detail'];
      } catch (_) {}
      throw ApiException(errorMsg, response.statusCode);
    } on SocketException {
      throw ApiException('Offline mode active. Connection required for analysis.');
    } catch (e) {
      if (e is ApiException) rethrow;
      if (e.toString().contains('SocketException') || e.toString().contains('Connection refused')) {
        throw ApiException('Offline mode active. Connection required for analysis.');
      }
      throw ApiException(e.toString());
    }
  }

  Future<AnalysisResult> checkUrl(String url) async {
    try {
      final response = await _client.post(
        Uri.parse(ApiConfig.checkUrlEndpoint),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'url': url}),
      ).timeout(ApiConfig.requestTimeout);
      if (response.statusCode == 200) return AnalysisResult.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
      
      String errorMsg = 'Failed to analyze URL (Status ${response.statusCode})';
      try {
        final decoded = jsonDecode(response.body);
        if (decoded['detail'] != null) errorMsg = decoded['detail'];
      } catch (_) {}
      throw ApiException(errorMsg, response.statusCode);
    } on SocketException {
      throw ApiException('Offline mode active. Connection required for analysis.');
    } catch (e) {
      if (e is ApiException) rethrow;
      if (e.toString().contains('SocketException') || e.toString().contains('Connection refused')) {
        throw ApiException('Offline mode active. Connection required for analysis.');
      }
      throw ApiException(e.toString());
    }
  }

  Future<AnalysisResult> checkImage(List<int> bytes, String filename) async {
    try {
      var request = http.MultipartRequest('POST', Uri.parse('${ApiConfig.baseUrl}/check-image'));
      final ext = filename.split('.').last.toLowerCase();
      final mimeType = ext == 'png' ? 'png' : (ext == 'webp' ? 'webp' : 'jpeg');
      request.files.add(http.MultipartFile.fromBytes(
        'file', bytes, 
        filename: filename,
        contentType: MediaType('image', mimeType)
      ));
      var response = await _client.send(request).timeout(ApiConfig.requestTimeout);
      var responseBody = await response.stream.bytesToString();
      if (response.statusCode == 200) return AnalysisResult.fromJson(jsonDecode(responseBody) as Map<String, dynamic>);
      
      String errorMsg = 'Failed to analyze image (Status ${response.statusCode})';
      try {
        final decoded = jsonDecode(responseBody);
        if (decoded['detail'] != null) errorMsg = decoded['detail'];
      } catch (_) {}
      throw ApiException(errorMsg, response.statusCode);
    } on SocketException {
      throw ApiException('Offline mode active. Connection required for analysis.');
    } catch (e) {
      if (e is ApiException) rethrow;
      if (e.toString().contains('SocketException') || e.toString().contains('Connection refused')) {
        throw ApiException('Offline mode active. Connection required for analysis.');
      }
      throw ApiException(e.toString());
    }
  }

  Future<AnalysisResult> checkVideo(List<int> bytes, String filename) async {
    try {
      var request = http.MultipartRequest('POST', Uri.parse('${ApiConfig.baseUrl}/check-video'));
      final ext = filename.split('.').last.toLowerCase();
      final mimeType = ext == 'webm' ? 'webm' : (ext == 'mov' ? 'quicktime' : 'mp4');
      request.files.add(http.MultipartFile.fromBytes(
        'file', bytes, 
        filename: filename,
        contentType: MediaType('video', mimeType)
      ));
      var response = await _client.send(request).timeout(const Duration(minutes: 2));
      var responseBody = await response.stream.bytesToString();
      if (response.statusCode == 200) return AnalysisResult.fromJson(jsonDecode(responseBody) as Map<String, dynamic>);
      
      String errorMsg = 'Failed to analyze video (Status ${response.statusCode})';
      try {
        final decoded = jsonDecode(responseBody);
        if (decoded['detail'] != null) errorMsg = decoded['detail'];
      } catch (_) {}
      throw ApiException(errorMsg, response.statusCode);
    } on SocketException {
      throw ApiException('Offline mode active. Connection required for analysis.');
    } catch (e) {
      if (e is ApiException) rethrow;
      if (e.toString().contains('SocketException') || e.toString().contains('Connection refused')) {
        throw ApiException('Offline mode active. Connection required for analysis.');
      }
      throw ApiException(e.toString());
    }
  }

  Future<ResearchResult> researchClaim(String claim) async {
    try {
      final response = await _client.post(
        Uri.parse(ApiConfig.researchEndpoint),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'claim': claim}),
      ).timeout(ApiConfig.requestTimeout);
      if (response.statusCode == 200) return ResearchResult.fromJson(jsonDecode(response.body));
      throw ApiException('Failed to perform research');
    } on SocketException {
      throw ApiException('Offline mode active. Connection required for analysis.');
    } catch (e) {
      if (e.toString().contains('SocketException') || e.toString().contains('Connection refused')) {
        throw ApiException('Offline mode active. Connection required for analysis.');
      }
      throw ApiException(e.toString());
    }
  }

  Future<NewsResponse> fetchNews({bool forceRefresh = false}) async {
    try {
      final uri = forceRefresh 
          ? Uri.parse('${ApiConfig.newsEndpoint}?force_refresh=true')
          : Uri.parse(ApiConfig.newsEndpoint);
      final response = await _client.get(uri).timeout(ApiConfig.requestTimeout);
      if (response.statusCode == 200) {
        final newsResp = NewsResponse.fromJson(jsonDecode(response.body));
        await StorageService.cacheNews(newsResp);
        return newsResp;
      }
      throw ApiException('Failed to fetch news');
    } catch (e) {
      throw ApiException(e.toString());
    }
  }

  Future<List<HistoryItem>> fetchHistory() async {
    return await StorageService.getHistory();
  }

  Future<void> saveHistory({
    required String textSnippet,
    required String verdict,
    int? confidence,
    required String summary,
    required String inputType,
    AnalysisResult? analysisResult,
  }) async {
    final item = HistoryItem(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      inputType: inputType,
      textSnippet: textSnippet,
      verdict: VerdictType.fromString(verdict),
      confidence: confidence,
      summary: summary,
      analysisResult: analysisResult,
      timestamp: DateTime.now().toIso8601String(),
    );
    await StorageService.saveHistoryItem(item);
  }
  
  Future<void> deleteHistory(String id) async {
    await StorageService.deleteHistoryItem(id);
  }

  Future<void> clearAllHistory() async {
    await StorageService.clearHistory();
  }

  Future<CommunityReport> submitReport({
    required String category,
    required String verdict,
    required String contentSummary,
    String? comment,
    String? sourceUrl,
    required String inputType,
  }) async {
    try {
      final response = await _client.post(
        Uri.parse('${ApiConfig.baseUrl}/reports'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'category': category,
          'verdict': verdict,
          'content_summary': contentSummary,
          'comment': comment,
          'source_url': sourceUrl,
          'input_type': inputType,
        }),
      ).timeout(ApiConfig.requestTimeout);
      
      if (response.statusCode == 200) {
        return CommunityReport.fromJson(jsonDecode(response.body));
      } else {
        throw ApiException('Failed to submit report');
      }
    } on SocketException {
      throw ApiException('Offline mode active. Cannot submit reports without a connection.');
    } catch (e) {
      if (e.toString().contains('SocketException') || e.toString().contains('Connection refused')) {
        throw ApiException('Offline mode active. Cannot submit reports without a connection.');
      }
      throw ApiException(e.toString());
    }
  }

  Future<List<CommunityReport>> getReports() async {
    try {
      final response = await _client.get(
        Uri.parse('${ApiConfig.baseUrl}/reports'),
      ).timeout(ApiConfig.requestTimeout);
      
      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        final reports = data.map((json) => CommunityReport.fromJson(json)).toList();
        await StorageService.cacheReports(reports);
        return reports;
      } else {
        throw ApiException('Failed to fetch reports');
      }
    } catch (e) {
      final cached = await StorageService.getCachedReports();
      if (cached.isNotEmpty) {
        return cached;
      }
      if (e.toString().contains('SocketException') || e.toString().contains('Connection refused')) {
        throw ApiException('Offline mode active. No cached reports available.');
      }
      throw ApiException(e.toString());
    }
  }
}
