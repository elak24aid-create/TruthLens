import 'package:flutter/foundation.dart' show kIsWeb, kReleaseMode;

class ApiConfig {
  static const String productionUrl = 'https://truthlens-l1vq.onrender.com/api';

  static String get baseUrl {
    const envUrl = String.fromEnvironment('API_BASE_URL');
    if (envUrl.isNotEmpty) return envUrl;
    
    return productionUrl;
  }

  static String get healthEndpoint => '$baseUrl/health';
  static String get checkTextEndpoint => '$baseUrl/check-text';
  static String get checkUrlEndpoint => '$baseUrl/check-url';
  static String get historyEndpoint => '$baseUrl/history';
  static String get researchEndpoint => '$baseUrl/research';
  static String get newsEndpoint => '$baseUrl/news';

  static const Duration requestTimeout = Duration(seconds: 15);
}
