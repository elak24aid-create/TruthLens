import 'verdict.dart';
import 'analysis_result.dart';
import 'research_result.dart';

class HistoryItem {
  final String id;
  final String timestamp;
  final String textSnippet;
  final VerdictType verdict;
  final int confidence;
  final String summary;
  final String inputType;
  final String? url;
  final AnalysisResult? analysisResult;
  final ResearchResult? researchResult;

  const HistoryItem({
    required this.id,
    required this.timestamp,
    required this.textSnippet,
    required this.verdict,
    required this.confidence,
    required this.summary,
    required this.inputType,
    this.url,
    this.analysisResult,
    this.researchResult,
  });

  factory HistoryItem.fromJson(Map<String, dynamic> json) {
    return HistoryItem(
      id: json['id'] as String? ?? '',
      timestamp: json['timestamp'] as String? ?? '',
      textSnippet: json['text_snippet'] as String? ?? '',
      verdict: VerdictType.fromString(json['verdict'] as String? ?? 'Unverified'),
      confidence: (json['confidence'] as num?)?.toInt() ?? 50,
      summary: json['summary'] as String? ?? '',
      inputType: json['input_type'] as String? ?? 'text',
      url: json['url'] as String?,
      analysisResult: json['analysis_result'] != null ? AnalysisResult.fromJson(json['analysis_result'] as Map<String, dynamic>) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'timestamp': timestamp,
      'text_snippet': textSnippet,
      'verdict': verdict.displayName,
      'confidence': confidence,
      'summary': summary,
      'input_type': inputType,
      'url': url,
      'analysis_result': analysisResult?.toJson(),
      'research_result': researchResult?.toJson(),
    };
  }
}
