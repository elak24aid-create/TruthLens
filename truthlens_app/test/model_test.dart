import 'package:flutter_test/flutter_test.dart';
import 'package:truthlens_app/models/verdict.dart';
import 'package:truthlens_app/models/analysis_result.dart';
import 'package:truthlens_app/models/signal_item.dart';
import 'package:truthlens_app/models/history_item.dart';

void main() {
  group('VerdictType Tests', () {
    test('Correctly maps strings to VerdictType enum', () {
      expect(VerdictType.fromString('Likely Genuine'), VerdictType.likelyGenuine);
      expect(VerdictType.fromString('Likely Misleading'), VerdictType.likelyMisleading);
      expect(VerdictType.fromString('Satire'), VerdictType.satire);
      expect(VerdictType.fromString('Insufficient Evidence'), VerdictType.insufficientEvidence);
      expect(VerdictType.fromString('Unverified'), VerdictType.unverified);
      expect(VerdictType.fromString('Unknown random string'), VerdictType.unverified);
    });
  });

  group('AnalysisResult JSON Parsing', () {
    test('Parses backend AnalysisResult JSON payload correctly', () {
      final json = {
        'verdict': 'Likely Misleading',
        'confidence': 78,
        'language': 'English',
        'summary': 'Available signals indicate patterns commonly associated with misleading claims.',
        'why_this_verdict': [
          'Content displays sensationalist stylistic patterns.',
          'Source could not be verified.',
        ],
        'signals': [
          {
            'category': 'Content Signals',
            'status': 'found',
            'label': 'Stylistic Red Flags',
            'score': 85,
            'explanation': 'Excessive uppercase and buzzwords detected.',
          },
          {
            'category': 'Source Information',
            'status': 'not_found',
            'label': 'Unattributed Source',
            'score': null,
            'explanation': 'No verified domain identified.',
          }
        ],
        'evidence': [],
        'analyzed_at': '2026-09-21T08:00:00Z',
      };

      final result = AnalysisResult.fromJson(json);

      expect(result.verdict, VerdictType.likelyMisleading);
      expect(result.confidence, 78);
      expect(result.language, 'English');
      expect(result.whyThisVerdict.length, 2);
      expect(result.signals.length, 2);
      expect(result.signals[0].isFound, true);
      expect(result.signals[1].isNotFound, true);
    });
  });

  group('HistoryItem Tests', () {
    test('Parses HistoryItem JSON correctly', () {
      final json = {
        'id': 'test-uuid-1234',
        'timestamp': '2026-09-21T08:00:00Z',
        'text_snippet': 'Sample suspicious news snippet',
        'verdict': 'Likely Genuine',
        'confidence': 88,
        'summary': 'Summary of genuine check',
        'input_type': 'text',
      };

      final item = HistoryItem.fromJson(json);
      expect(item.id, 'test-uuid-1234');
      expect(item.verdict, VerdictType.likelyGenuine);
      expect(item.confidence, 88);
    });
  });
}
