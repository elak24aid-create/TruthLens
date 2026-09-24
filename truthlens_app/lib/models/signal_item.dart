class SignalItem {
  final String category;
  final String status; // 'found', 'not_found', 'conflicting'
  final String label;
  final int? score;
  final String explanation;

  const SignalItem({
    required this.category,
    required this.status,
    required this.label,
    this.score,
    required this.explanation,
  });

  factory SignalItem.fromJson(Map<String, dynamic> json) {
    return SignalItem(
      category: json['category'] as String? ?? 'General Signal',
      status: json['status'] as String? ?? 'not_found',
      label: json['label'] as String? ?? '',
      score: json['score'] as int?,
      explanation: json['explanation'] as String? ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'category': category,
      'status': status,
      'label': label,
      'score': score,
      'explanation': explanation,
    };
  }

  bool get isFound => status == 'found';
  bool get isConflicting => status == 'conflicting';
  bool get isNotFound => status == 'not_found';
}
