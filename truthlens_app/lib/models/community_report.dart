class CommunityReport {
  final String id;
  final String category;
  final String verdict;
  final String contentSummary;
  final String? comment;
  final String? sourceUrl;
  final String inputType;
  final String status;
  final String submittedAt;

  CommunityReport({
    required this.id,
    required this.category,
    required this.verdict,
    required this.contentSummary,
    this.comment,
    this.sourceUrl,
    required this.inputType,
    required this.status,
    required this.submittedAt,
  });

  factory CommunityReport.fromJson(Map<String, dynamic> json) {
    return CommunityReport(
      id: json['id'] as String,
      category: json['category'] as String,
      verdict: json['verdict'] as String,
      contentSummary: json['content_summary'] as String,
      comment: json['comment'] as String?,
      sourceUrl: json['source_url'] as String?,
      inputType: json['input_type'] as String,
      status: json['status'] as String,
      submittedAt: json['submitted_at'] as String,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'category': category,
      'verdict': verdict,
      'content_summary': contentSummary,
      'comment': comment,
      'source_url': sourceUrl,
      'input_type': inputType,
      'status': status,
      'submitted_at': submittedAt,
    };
  }
}
