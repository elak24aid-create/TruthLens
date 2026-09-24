class EvidenceItem {
  final String source;
  final String title;
  final String? url;
  final String? date;
  final String relationship; // 'supporting', 'conflicting', 'context'
  final String explanation;

  const EvidenceItem({
    required this.source,
    required this.title,
    this.url,
    this.date,
    required this.relationship,
    required this.explanation,
  });

  factory EvidenceItem.fromJson(Map<String, dynamic> json) {
    return EvidenceItem(
      source: json['source'] as String? ?? 'Unknown Source',
      title: json['title'] as String? ?? '',
      url: json['url'] as String?,
      date: json['date'] as String?,
      relationship: json['relationship'] as String? ?? 'context',
      explanation: json['explanation'] as String? ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'source': source,
      'title': title,
      'url': url,
      'date': date,
      'relationship': relationship,
      'explanation': explanation,
    };
  }
}
