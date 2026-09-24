import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'share_helper.dart';
import '../../models/analysis_result.dart';
import '../../widgets/verdict_badge.dart';
import 'report_screen.dart';
import '../../widgets/confidence_gauge.dart';
import '../../widgets/why_verdict_card.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_strings.dart';
import '../../services/api_service.dart';
import '../../services/local_history_service.dart';
import '../../models/history_item.dart';
import '../../models/research_result.dart';
import 'package:url_launcher/url_launcher.dart';

class ResultScreen extends StatefulWidget {
  final AnalysisResult result;
  final String originalText;
  final String inputType;
  final bool isHistory;
  final String? historyTimestamp;
  final ResearchResult? historyResearchResult;

  const ResultScreen({
    super.key,
    required this.result,
    required this.originalText,
    this.inputType = 'text',
    this.isHistory = false,
    this.historyTimestamp,
    this.historyResearchResult,
  });

  @override
  State<ResultScreen> createState() => _ResultScreenState();
}

class _ResultScreenState extends State<ResultScreen> {
  final ApiService _apiService = ApiService();
  final LocalHistoryService _localHistoryService = LocalHistoryService();
  bool _isSaved = false;
  
  bool _isResearching = false;
  ResearchResult? _researchResult;
  String? _researchError;

  @override
  void initState() {
    super.initState();
    if (widget.isHistory && widget.historyResearchResult != null) {
      _researchResult = widget.historyResearchResult;
      _isResearching = false;
    } else if (widget.isHistory && widget.historyResearchResult == null) {
      _isResearching = false;
    } else {
      _performResearch();
    }
  }

  Future<void> _performResearch() async {
    setState(() {
      _isResearching = true;
      _researchError = null;
    });
    
    try {
      final claimText = widget.result.extractedMetadata?['claim_text'] ?? widget.originalText;
      final res = await _apiService.researchClaim(claimText);
      if (mounted) {
        setState(() {
          _researchResult = res;
          _isResearching = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _researchError = e.toString();
          _isResearching = false;
        });
      }
    }
  }

  Future<void> _saveToHistory() async {
    if (_isSaved) return;

    // Save to local storage
    final localItem = HistoryItem(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      timestamp: DateTime.now().toIso8601String(),
      textSnippet: widget.originalText.length > 150
          ? '${widget.originalText.substring(0, 150)}...'
          : widget.originalText,
      verdict: widget.result.verdict,
      confidence: widget.result.confidence,
      summary: widget.result.summary,
      inputType: widget.inputType,
    );
    await _localHistoryService.saveLocalItem(localItem);

    // Save to backend API
    await _apiService.saveHistory(
      textSnippet: localItem.textSnippet,
      verdict: widget.result.verdict.displayName,
      confidence: widget.result.confidence,
      summary: widget.result.summary,
      inputType: widget.inputType,
    );

    if (mounted) {
      setState(() {
        _isSaved = true;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Analysis saved to History.'),
          behavior: SnackBarBehavior.floating,
        ),
      );
    }
  }


  Widget _buildSourceItem(ResearchSource source, bool isDark) {
    IconData icon;
    Color iconColor;
    if (source.direction == 'supporting') {
      icon = Icons.check_circle;
      iconColor = AppColors.verdictGenuine;
    } else if (source.direction == 'contradicting') {
      icon = Icons.warning;
      iconColor = AppColors.verdictMisleading;
    } else {
      icon = Icons.info;
      iconColor = Colors.blueGrey;
    }

    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isDark ? const Color(0xFF1E293B) : const Color(0xFFF8FAFC),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: isDark ? const Color(0xFF334155) : const Color(0xFFE2E8F0),
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, size: 16, color: iconColor),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    source.title,
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.bold,
                      color: isDark ? AppColors.textPrimaryDark : AppColors.textPrimaryLight,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 4),
            Text(
              '${source.sourceName} • ${source.direction.toUpperCase()}',
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                color: isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              source.snippet,
              style: TextStyle(
                fontSize: 12,
                height: 1.4,
                color: isDark ? AppColors.textPrimaryDark : AppColors.textPrimaryLight,
              ),
            ),
            const SizedBox(height: 8),
            InkWell(
              onTap: () async {
                final url = Uri.parse(source.url);
                if (await canLaunchUrl(url)) {
                  await launchUrl(url);
                }
              },
              child: const Text(
                'Open Source',
                style: TextStyle(
                  fontSize: 12,
                  color: AppColors.primaryLight,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _openReport() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => ReportScreen(
          result: widget.result,
          inputType: widget.inputType,
          originalText: widget.originalText,
          isHistory: widget.isHistory,
          historyTimestamp: widget.historyTimestamp,
          researchResult: _researchResult,
        ),
      ),
    );
  }

  String _generateDynamicExplanation() {
    final verdict = widget.result.verdict.displayName;
    final conf = widget.result.confidence;
    final r = _researchResult;
    int supporting = 0;
    int contradicting = 0;
    
    if (r != null) {
      supporting = r.sources.where((s) => s.direction == 'supporting').length;
      contradicting = r.sources.where((s) => s.direction == 'contradicting').length;
    }

    String explanation = "The ML model classified this content as $verdict with a confidence of $conf%. ";
    if (r == null || _isResearching) {
      explanation += "Online research is currently unavailable or still processing. ";
    } else if (r.sources.isEmpty) {
      explanation += "Online research found 0 external evidence sources. ";
    } else {
      explanation += "Online research found ${r.sources.length} relevant sources. ";
      if (supporting > 0 && contradicting == 0) {
        explanation += "These sources generally provided information supporting the claims. ";
      } else if (contradicting > 0 && supporting == 0) {
        explanation += "These sources generally provided information contradicting or debunking the claims. ";
      } else if (supporting > 0 && contradicting > 0) {
        explanation += "These sources provided a mix of supporting and contradicting information. ";
      } else {
        explanation += "These sources provided neutral background context without definitively proving or disproving the claims. ";
      }
    }
    explanation += "Please note: this result should be treated as an automated probabilistic assessment rather than absolute proof.";
    return explanation;
  }


  String _buildShareText() {
    final buffer = StringBuffer();
    buffer.writeln('TRUTHLENS VERIFICATION');
    buffer.writeln();
    buffer.writeln('Verdict: ${widget.result.verdict.displayName}');
    buffer.writeln('ML Confidence: ${widget.result.confidence}%');
    buffer.writeln('Input Type: ${widget.inputType.toUpperCase()}');
    buffer.writeln();
    buffer.writeln('Why This Verdict:');
    buffer.writeln(_generateDynamicExplanation());
    buffer.writeln();
    if (_researchResult != null) {
      buffer.writeln('Online Evidence: ${_researchResult!.sources.length} available sources');
    }
    buffer.writeln();
    buffer.writeln('Limitations:');
    buffer.writeln('ML classification is probabilistic. Online evidence may be incomplete. Source availability does not prove truth. Lack of evidence does not mean false. The system may make mistakes. Media OCR only analyzes extracted text, not manipulation.');
    buffer.writeln();
    buffer.writeln('Checked with TruthLens.');
    return buffer.toString();
  }

  Future<void> _copySummary() async {
    final text = _buildShareText();
    await Clipboard.setData(ClipboardData(text: text));
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Summary copied to clipboard.'), behavior: SnackBarBehavior.floating),
      );
    }
  }

  Future<void> _shareResult() async {
    final text = _buildShareText();
    bool shared = await shareTextWeb('TruthLens Verification Result', text);
    if (!shared) {
      await _copySummary();
    }
  }

  void _showReportDialog() {
    String selectedReason = 'Incorrect verdict';
    final TextEditingController commentController = TextEditingController();
    bool isSubmitting = false;

    showDialog(
      context: context,
      builder: (ctx) {
        return StatefulBuilder(
          builder: (context, setStateDialog) {
            return AlertDialog(
              title: const Text('Report Result'),
              content: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Why are you reporting this result?', style: TextStyle(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    DropdownButtonFormField<String>(
                      value: selectedReason,
                      isExpanded: true,
                      items: ['Incorrect verdict', 'Misleading result', 'Missing evidence', 'Incorrect source information', 'Other']
                          .map((r) => DropdownMenuItem(value: r, child: Text(r)))
                          .toList(),
                      onChanged: (val) {
                        setStateDialog(() {
                          if (val != null) selectedReason = val;
                        });
                      },
                    ),
                    const SizedBox(height: 16),
                    const Text('Additional comments (optional):', style: TextStyle(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    TextField(
                      controller: commentController,
                      maxLines: 3,
                      maxLength: 500,
                      decoration: const InputDecoration(
                        border: OutlineInputBorder(),
                        hintText: 'Provide details...',
                      ),
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: isSubmitting ? null : () => Navigator.pop(ctx),
                  child: const Text('Cancel'),
                ),
                ElevatedButton(
                  onPressed: isSubmitting ? null : () async {
                    setStateDialog(() => isSubmitting = true);
                    try {
                      String contentSummary = widget.originalText;
                      if (contentSummary.length > 200) contentSummary = '${contentSummary.substring(0, 200)}...';
                      
                      await _apiService.submitReport(
                        category: selectedReason,
                        verdict: widget.result.verdict.displayName,
                        contentSummary: contentSummary,
                        comment: commentController.text.trim(),
                        inputType: widget.inputType,
                      );
                      if (mounted) {
                        Navigator.pop(ctx);
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Thank you. Your report has been submitted.'), behavior: SnackBarBehavior.floating),
                        );
                      }
                    } catch (e) {
                      if (mounted) {
                        setStateDialog(() => isSubmitting = false);
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Failed to submit report. Please try again.'), behavior: SnackBarBehavior.floating, backgroundColor: Colors.red),
                        );
                      }
                    }
                  },
                  child: isSubmitting ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2)) : const Text('Submit Report'),
                ),
              ],
            );
          },
        );
      },
    );
  }

  Widget _buildSectionHeader(String title, IconData icon) {
    return Row(
      children: [
        Icon(icon, size: 20, color: AppColors.primaryLight),
        const SizedBox(width: 8),
        Text(
          title,
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final result = widget.result;

    List<ResearchSource> supportingSources = [];
    List<ResearchSource> contradictingSources = [];
    List<ResearchSource> neutralSources = [];
    
    if (_researchResult != null) {
      supportingSources = _researchResult!.sources.where((s) => s.direction == 'supporting').toList();
      contradictingSources = _researchResult!.sources.where((s) => s.direction == 'contradicting').toList();
      neutralSources = _researchResult!.sources.where((s) => s.direction == 'neutral').toList();
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Analysis Result', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
        actions: [
          IconButton(
            icon: const Icon(Icons.description_outlined),
            tooltip: 'View Report',
            onPressed: _openReport,
          ),
          IconButton(
            icon: Icon(
              _isSaved ? Icons.bookmark : Icons.bookmark_border,
              color: _isSaved ? AppColors.primaryLight : null,
            ),
            tooltip: 'Save to History',
            onPressed: _saveToHistory,
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (widget.isHistory)
              Container(
                margin: const EdgeInsets.only(bottom: 16),
                color: Colors.orange.withValues(alpha: 0.2),
                padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
                child: Row(
                  children: [
                    const Icon(Icons.history, color: Colors.orange, size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Historical Result — Generated on ${widget.historyTimestamp ?? 'a previous date'}',
                        style: const TextStyle(color: Colors.orange, fontWeight: FontWeight.bold, fontSize: 12),
                      ),
                    ),
                  ],
                ),
              ),

            // Header Verdict Card
            Card(
              child: Container(
                padding: const EdgeInsets.all(20.0),
                decoration: BoxDecoration(
                  color: result.verdict.backgroundColor,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: result.verdict.color.withValues(alpha: 0.3),
                    width: 1.5,
                  ),
                ),
                child: Column(
                  children: [
                    VerdictBadge(verdict: result.verdict, isLarge: true),
                    const SizedBox(height: 16),
                    ConfidenceGauge(
                      confidence: result.confidence,
                      activeColor: result.verdict.color,
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // 1. ML Analysis
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildSectionHeader('ML Analysis', Icons.psychology),
                    const SizedBox(height: 12),
                    Text(
                      'Predicted Class: ${result.verdict.displayName}',
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Confidence: ${result.confidence}%',
                      style: const TextStyle(fontSize: 14),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Explanation: ${result.summary}',
                      style: TextStyle(
                        fontSize: 13,
                        color: isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // 2. Source Information / Extracted Content
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildSectionHeader(widget.inputType == 'url' ? 'Source Information' : 'Extracted Content', widget.inputType == 'url' ? Icons.newspaper : Icons.document_scanner),
                    const SizedBox(height: 12),
                    if (result.extractedMetadata != null) ...[
                      if (result.extractedMetadata!['title'] != null)
                        Padding(
                          padding: const EdgeInsets.only(bottom: 4),
                          child: Text('Title: ${result.extractedMetadata!['title']}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                        ),
                      if (result.extractedMetadata!['source_name'] != null)
                        Padding(
                          padding: const EdgeInsets.only(bottom: 4),
                          child: Text('Publisher: ${result.extractedMetadata!['source_name']}', style: const TextStyle(fontSize: 13)),
                        ),
                      if (widget.inputType == 'video')
                        Padding(
                          padding: const EdgeInsets.only(bottom: 4),
                          child: Text('Video Duration: ${result.extractedMetadata!['duration_sec'] ?? '?'}s | Frames: ${result.extractedMetadata!['frames_sampled'] ?? '?'}', style: const TextStyle(fontSize: 13)),
                        ),
                      if (result.extractedMetadata!['ocr_text'] != null)
                        Padding(
                          padding: const EdgeInsets.only(top: 8, bottom: 4),
                          child: Text('OCR Text:', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                        ),
                    ],
                    Text(
                      widget.originalText,
                      maxLines: 4,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                        fontSize: 13,
                        fontStyle: FontStyle.italic,
                        color: isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // 3. Why This Verdict?
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildSectionHeader('Why This Verdict?', Icons.lightbulb_outline),
                    const SizedBox(height: 12),
                    Text(
                      _generateDynamicExplanation(),
                      style: TextStyle(
                        fontSize: 14,
                        height: 1.5,
                        color: isDark ? AppColors.textPrimaryDark : AppColors.textPrimaryLight,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // 4. Online Evidence
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildSectionHeader('Online Evidence', Icons.travel_explore),
                    const SizedBox(height: 16),
                    if (_isResearching)
                      const Center(
                        child: Padding(
                          padding: EdgeInsets.all(16.0),
                          child: CircularProgressIndicator(),
                        ),
                      )
                    else if (_researchError != null)
                      Text(
                        'Research failed: ${_researchError}',
                        style: const TextStyle(color: Colors.red),
                      )
                    else if (_researchResult != null)
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            _researchResult!.summary,
                            style: TextStyle(
                              fontSize: 13,
                              height: 1.4,
                              color: isDark ? AppColors.textPrimaryDark : AppColors.textPrimaryLight,
                            ),
                          ),
                          const SizedBox(height: 16),
                          if (supportingSources.isNotEmpty) ...[
                            Row(children: const [Icon(Icons.check_circle, size: 16, color: AppColors.verdictGenuine), SizedBox(width: 8), Text('Supporting Evidence', style: TextStyle(fontWeight: FontWeight.bold))]),
                            const SizedBox(height: 8),
                            ...supportingSources.map((s) => _buildSourceItem(s, isDark)).toList(),
                          ],
                          if (contradictingSources.isNotEmpty) ...[
                            Row(children: const [Icon(Icons.warning, size: 16, color: AppColors.verdictMisleading), SizedBox(width: 8), Text('Contradicting Evidence', style: TextStyle(fontWeight: FontWeight.bold))]),
                            const SizedBox(height: 8),
                            ...contradictingSources.map((s) => _buildSourceItem(s, isDark)).toList(),
                          ],
                          if (neutralSources.isNotEmpty) ...[
                            Row(children: const [Icon(Icons.info, size: 16, color: Colors.blueGrey), SizedBox(width: 8), Text('Background / Neutral Evidence', style: TextStyle(fontWeight: FontWeight.bold))]),
                            const SizedBox(height: 8),
                            ...neutralSources.map((s) => _buildSourceItem(s, isDark)).toList(),
                          ],
                        ],
                      ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // 5. Limitations
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: isDark ? const Color(0xFF1E293B) : const Color(0xFFF1F5F9),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(
                  color: isDark ? const Color(0xFF334155) : const Color(0xFFE2E8F0),
                ),
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(Icons.warning_amber_rounded, size: 16, color: AppColors.textSecondaryLight),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'LIMITATIONS: ML classification is probabilistic. Online evidence may be incomplete. Source availability does not prove truth. Lack of evidence does not mean false. The system may make mistakes. Media OCR only analyzes extracted text, not manipulation.',
                      style: TextStyle(
                        fontSize: 11,
                        height: 1.4,
                        color: isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            // Actions row
            Wrap(
              spacing: 12,
              runSpacing: 12,
              alignment: WrapAlignment.center,
              children: [
                ElevatedButton.icon(
                  onPressed: () => Navigator.pop(context),
                  icon: const Icon(Icons.refresh, size: 18),
                  label: const Text('Check Another'),
                ),
                OutlinedButton.icon(
                  onPressed: _shareResult,
                  icon: const Icon(Icons.share, size: 18),
                  label: const Text('Share Result'),
                ),
                OutlinedButton.icon(
                  onPressed: _copySummary,
                  icon: const Icon(Icons.copy, size: 18),
                  label: const Text('Copy Summary'),
                ),
                TextButton.icon(
                  onPressed: _showReportDialog,
                  icon: const Icon(Icons.flag_outlined, size: 18, color: Colors.redAccent),
                  label: const Text('Report This Result', style: TextStyle(color: Colors.redAccent)),
                ),
              ],
            ),
            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }
}
