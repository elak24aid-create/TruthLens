class EvidenceItem {
  final String publisher;
  final String title;
  final String? url;
  final String? publishedDate;
  final String relationship; // 'supporting', 'conflicting', 'context', 'unrelated'
  final String? evidenceExcerpt;
  
  // Legacy mappings
  final String? legacySource;
  final String? legacyDate;
  final String? legacyExplanation;

  const EvidenceItem({
    required this.publisher,
    required this.title,
    this.url,
    this.publishedDate,
    required this.relationship,
    this.evidenceExcerpt,
    this.legacySource,
    this.legacyDate,
    this.legacyExplanation,
  });

  factory EvidenceItem.fromJson(Map<String, dynamic> json) {
    return EvidenceItem(
      publisher: json['publisher'] as String? ?? json['source'] as String? ?? 'Unknown Publisher',
      title: json['title'] as String? ?? '',
      url: json['url'] as String?,
      publishedDate: json['published_date'] as String? ?? json['date'] as String?,
      relationship: json['relationship'] as String? ?? 'context',
      evidenceExcerpt: json['evidence_excerpt'] as String? ?? json['explanation'] as String?,
      legacySource: json['source'] as String?,
      legacyDate: json['date'] as String?,
      legacyExplanation: json['explanation'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'publisher': publisher,
      'title': title,
      'url': url,
      'published_date': publishedDate,
      'relationship': relationship,
      'evidence_excerpt': evidenceExcerpt,
      'source': legacySource ?? publisher,
      'date': legacyDate ?? publishedDate,
      'explanation': legacyExplanation ?? evidenceExcerpt,
    };
  }

  // Helper getters for UI
  String get displaySource => publisher;
  String get displayDate => publishedDate ?? '';
  String get displayExcerpt => evidenceExcerpt ?? '';
}
