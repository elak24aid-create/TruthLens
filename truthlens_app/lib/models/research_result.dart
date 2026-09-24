class ResearchSource {
  final String title;
  final String url;
  final String sourceName;
  final String snippet;
  final String direction;

  ResearchSource({
    required this.title,
    required this.url,
    required this.sourceName,
    required this.snippet,
    this.direction = 'neutral',
  });

  factory ResearchSource.fromJson(Map<String, dynamic> json) {
    return ResearchSource(
      title: json['title'] ?? '',
      url: json['url'] ?? '',
      sourceName: json['source_name'] ?? '',
      snippet: json['snippet'] ?? '',
      direction: json['direction'] ?? 'neutral',
    );
  }

  Map<String, dynamic> toJson() => {
    'title': title,
    'url': url,
    'source_name': sourceName,
    'snippet': snippet,
    'direction': direction,
  };
}

class ResearchResult {
  final String claim;
  final List<ResearchSource> sources;
  final String summary;
  final String status;

  ResearchResult({
    required this.claim,
    required this.sources,
    required this.summary,
    required this.status,
  });

  factory ResearchResult.fromJson(Map<String, dynamic> json) {
    var list = json['sources'] as List? ?? [];
    List<ResearchSource> sourcesList = list.map((i) => ResearchSource.fromJson(i)).toList();
    return ResearchResult(
      claim: json['claim'] ?? '',
      sources: sourcesList,
      summary: json['summary'] ?? '',
      status: json['research_status'] ?? 'error',
    );
  }

  Map<String, dynamic> toJson() => {
    'claim': claim,
    'sources': sources.map((s) => s.toJson()).toList(),
    'summary': summary,
    'research_status': status,
  };
}
