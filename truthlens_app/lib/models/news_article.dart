class NewsArticle {
  final String title;
  final String description;
  final String url;
  final String sourceName;
  final String publishedAt;
  final String? imageUrl;
  final String? category;

  NewsArticle({
    required this.title,
    required this.description,
    required this.url,
    required this.sourceName,
    required this.publishedAt,
    this.imageUrl,
    this.category,
  });

  factory NewsArticle.fromJson(Map<String, dynamic> json) {
    return NewsArticle(
      title: json['title'] ?? '',
      description: json['description'] ?? '',
      url: json['url'] ?? '',
      sourceName: json['source_name'] ?? '',
      publishedAt: json['published_at'] ?? '',
      imageUrl: json['image_url'],
      category: json['category'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'title': title,
      'description': description,
      'url': url,
      'source_name': sourceName,
      'published_at': publishedAt,
      'image_url': imageUrl,
      'category': category,
    };
  }
}

class NewsResponse {
  final List<NewsArticle> articles;
  final String updatedAt;
  final String status;

  NewsResponse({
    required this.articles,
    required this.updatedAt,
    required this.status,
  });

  factory NewsResponse.fromJson(Map<String, dynamic> json) {
    var list = json['articles'] as List? ?? [];
    List<NewsArticle> articlesList = list.map((i) => NewsArticle.fromJson(i)).toList();
    return NewsResponse(
      articles: articlesList,
      updatedAt: json['updated_at'] ?? '',
      status: json['status'] ?? 'error',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'articles': articles.map((a) => a.toJson()).toList(),
      'updated_at': updatedAt,
      'status': status,
    };
  }
}
