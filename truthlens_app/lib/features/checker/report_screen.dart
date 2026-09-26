import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'share_helper.dart';
import '../../models/analysis_result.dart';
import '../../core/constants/app_colors.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'download_helper.dart';


class ReportScreen extends StatelessWidget {
  final AnalysisResult result;
  final String inputType;
  final String originalText;
  final bool isHistory;
  final String? historyTimestamp;

  const ReportScreen({
    super.key,
    required this.result,
    required this.inputType,
    required this.originalText,
    this.isHistory = false,
    this.historyTimestamp,
  });

  String _generateReportText() {
    final buffer = StringBuffer();
    buffer.writeln('TRUTHLENS VERIFICATION REPORT');
    buffer.writeln('==============================');
    buffer.writeln();

    buffer.writeln('1. Check Information');
    buffer.writeln('   - Date/time: ${isHistory ? (historyTimestamp ?? result.analyzedAt) : result.analyzedAt}');
    buffer.writeln('   - Check type: ${inputType.toUpperCase()}');
    buffer.writeln('   - Input summary: ${originalText.replaceAll('\\n', ' ')}');
    buffer.writeln();

    buffer.writeln('2. ML Analysis');
    buffer.writeln('   - Model result: ${result.verdict.displayName}');
    buffer.writeln('   - Confidence: ${result.confidence ?? "N/A"}%');
    buffer.writeln('   - Explanation: ${result.summary}');
    buffer.writeln();

    buffer.writeln('3. Extracted Content');
    if (inputType == 'image' || inputType == 'video') {
      buffer.writeln('   - OCR text: ${result.extractedMetadata?['ocr_text']?.replaceAll('\\n', ' ') ?? 'None'}');
      if (inputType == 'video') {
        buffer.writeln('   - Duration: ${result.extractedMetadata?['duration_sec'] ?? 'Unknown'}s');
        buffer.writeln('   - Frames sampled: ${result.extractedMetadata?['frames_sampled'] ?? 0}');
      }
    } else if (inputType == 'url') {
      buffer.writeln('   - Article Title: ${result.extractedMetadata?['title'] ?? 'Unknown'}');
      buffer.writeln('   - Source: ${result.extractedMetadata?['source'] ?? 'Unknown'}');
    } else {
      buffer.writeln('   - Not applicable for this check type.');
    }
    buffer.writeln();

    buffer.writeln('4. Online Evidence');
    if (result.evidence.isEmpty) {
      buffer.writeln('   - Research summary: No external evidence found.');
    } else {
      buffer.writeln('   - Research summary: Found ${result.evidence.length} relevant sources.');
      for (int i = 0; i < result.evidence.length; i++) {
        final ev = result.evidence[i];
        buffer.writeln('     [${i + 1}] ${ev.title} (${ev.publisher})');
        buffer.writeln('         ${ev.url}');
      }
    }
    buffer.writeln();

    buffer.writeln('5. Why This Verdict?');
    for (final reason in result.whyThisVerdict) {
      buffer.writeln('   - $reason');
    }
    buffer.writeln();

    buffer.writeln('6. Limitations');
    buffer.writeln('   - ML classification is not proof of factual truth.');
    buffer.writeln('   - Online evidence is supporting information.');
    buffer.writeln('   - Image OCR analyzes extracted text, not image manipulation.');
    buffer.writeln('   - Video analysis analyzes sampled-frame text, not deepfake/manipulation status.');
    
    return buffer.toString();
  }

  Future<void> _copyReport(BuildContext context) async {
    final text = _generateReportText();
    await Clipboard.setData(ClipboardData(text: text));
    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Report copied to clipboard.'), behavior: SnackBarBehavior.floating),
      );
    }
  }

  Future<void> _shareReport(BuildContext context) async {
    final text = _generateReportText();
    bool shared = await shareTextWeb('TruthLens Verification Report', text);
    if (!shared) {
      await _copyReport(context);
    }
  }

  void _downloadReport(BuildContext context) {
    final text = _generateReportText();
    if (kIsWeb) {
      downloadTextFile(text, 'TruthLens_Report.txt');
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Report downloaded successfully')),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Export is currently only supported on Web.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final reportText = _generateReportText();
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Verification Report'),
        actions: [
          IconButton(
            icon: const Icon(Icons.copy),
            tooltip: 'Copy Report',
            onPressed: () => _copyReport(context),
          ),
          IconButton(
            icon: const Icon(Icons.share),
            tooltip: 'Share Report',
            onPressed: () => _shareReport(context),
          ),
          IconButton(
            icon: const Icon(Icons.download),
            tooltip: 'Download Text Report',
            onPressed: () => _downloadReport(context),
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16.0),
          decoration: BoxDecoration(
            color: isDark ? const Color(0xFF1E293B) : Colors.white,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: AppColors.borderLight),
          ),
          child: SingleChildScrollView(
            child: SelectableText(
              reportText,
              style: const TextStyle(
                fontFamily: 'Courier',
                fontSize: 13,
                height: 1.5,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
