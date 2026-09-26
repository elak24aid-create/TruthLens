import 'verdict.dart';
import 'signal_item.dart';
import 'evidence_item.dart';

class AnalysisResult {
  final VerdictType verdict;
  final int? confidence; // Made optional
  final String verificationMode; // Added
  final String language;
  final String summary;
  final List<String> whyThisVerdict;
  final List<SignalItem> signals;
  final List<EvidenceItem> evidence;
  final String analyzedAt;
  Map<String, dynamic>? extractedMetadata; // Made mutable to allow injection

  AnalysisResult({
    required this.verdict,
    this.confidence,
    this.verificationMode = 'WEB RESEARCH',
    required this.language,
    required this.summary,
    required this.whyThisVerdict,
    required this.signals,
    required this.evidence,
    required this.analyzedAt,
    this.extractedMetadata,
  });

  factory AnalysisResult.fromJson(Map<String, dynamic> json) {
    final rawVerdict = json['verdict'] as String? ?? 'Unverified';
    final signalsList = (json['signals'] as List<dynamic>?)
            ?.map((s) => SignalItem.fromJson(s as Map<String, dynamic>))
            .toList() ??
        [];
    final evidenceList = (json['evidence'] as List<dynamic>?)
            ?.map((e) => EvidenceItem.fromJson(e as Map<String, dynamic>))
            .toList() ??
        [];
    final whyList = (json['why_this_verdict'] as List<dynamic>?)
            ?.map((w) => w.toString())
            .toList() ??
        [];

    return AnalysisResult(
      verdict: VerdictType.fromString(rawVerdict),
      confidence: (json['confidence'] as num?)?.toInt(),
      verificationMode: json['verification_mode'] as String? ?? 'WEB RESEARCH',
      language: json['language'] as String? ?? 'English',
      summary: json['summary'] as String? ?? '',
      whyThisVerdict: whyList,
      signals: signalsList,
      evidence: evidenceList,
      analyzedAt: json['analyzed_at'] as String? ?? DateTime.now().toIso8601String(),
      extractedMetadata: json['extracted_metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'verdict': verdict.displayName,
      'confidence': confidence,
      'verification_mode': verificationMode,
      'language': language,
      'summary': summary,
      'why_this_verdict': whyThisVerdict,
      'signals': signals.map((s) => s.toJson()).toList(),
      'evidence': evidence.map((e) => e.toJson()).toList(),
      'analyzed_at': analyzedAt,
      'extracted_metadata': extractedMetadata,
    };
  }
}
