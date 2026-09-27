import 'dart:io' show Platform;
import 'package:flutter/foundation.dart' show kIsWeb, kReleaseMode;

class ApiConfig {
  static const String productionUrl = 'https://truthlens-l1vq.onrender.com/api';

  /// Resolves the appropriate local backend host based on the active platform:
  /// - Android emulator: 10.0.2.2 (special alias to host loopback interface)
  /// - Windows / Desktop / Web / iOS Simulator: 127.0.0.1
  static String get defaultHost {
    if (kIsWeb) return '127.0.0.1';
    try {
      if (Platform.isAndroid) return '10.0.2.2';
    } catch (_) {
      // Fallback if platform detection fails
      return '127.0.0.1';
    }
    return '127.0.0.1';
  }

  static String get baseUrl {
    const envUrl = String.fromEnvironment('API_BASE_URL');
    if (envUrl.isNotEmpty) return envUrl;
    
    // Use production URL if built in release mode, otherwise use local dev host
    if (kReleaseMode) {
      return productionUrl;
    }
    return 'http://$defaultHost:8000/api';
  }

  static String get healthEndpoint => '$baseUrl/health';
  static String get checkTextEndpoint => '$baseUrl/check-text';
  static String get checkUrlEndpoint => '$baseUrl/check-url';
  static String get historyEndpoint => '$baseUrl/history';
  static String get researchEndpoint => '$baseUrl/research';
  static String get newsEndpoint => '$baseUrl/news';

  static const Duration requestTimeout = Duration(seconds: 15);
}
