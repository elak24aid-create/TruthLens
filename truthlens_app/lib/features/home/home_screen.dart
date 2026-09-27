import 'dart:async';
import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_strings.dart';
import '../../services/api_service.dart';
import '../../services/storage_service.dart';

import 'package:url_launcher/url_launcher.dart';
import '../../models/news_article.dart';

class HomeScreen extends StatefulWidget {
  final VoidCallback onCheckNewsPressed;
  final Function(String) onCheckText;

  const HomeScreen({super.key, required this.onCheckNewsPressed, required this.onCheckText});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with WidgetsBindingObserver {
  final ApiService _apiService = ApiService();
  bool _isServerConnected = false;
  bool _isCheckingHealth = true;
  
  bool _isFetchingNews = false;
  NewsResponse? _newsResponse;
  String? _newsError;
  DateTime? _lastFetchTime;
  Timer? _refreshTimer;
  String _selectedCategory = 'All';
  final TextEditingController _searchController = TextEditingController();
  final List<String> _categories = ['All', 'India', 'World', 'Technology', 'Science', 'Sports', 'Business', 'Health'];

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _checkServerStatus();
    _fetchNews();
    _startRefreshTimer();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _refreshTimer?.cancel();
    _searchController.dispose();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      if (_lastFetchTime == null || DateTime.now().difference(_lastFetchTime!).inMinutes >= 15) {
        _fetchNews(forceRefresh: true);
      }
    }
  }

  void _startRefreshTimer() {
    _refreshTimer?.cancel();
    _refreshTimer = Timer.periodic(const Duration(minutes: 15), (timer) {
      _fetchNews(forceRefresh: true);
    });
  }

  Future<void> _fetchNews({bool forceRefresh = false}) async {
    setState(() {
      _isFetchingNews = true;
      _newsError = null;
    });
    
    try {
      final res = await _apiService.fetchNews(
        forceRefresh: forceRefresh,
        query: _searchController.text,
        category: _selectedCategory,
      );
      if (mounted) {
        if (forceRefresh && _newsResponse != null) {
          final oldTitles = _newsResponse!.articles.map((a) => a.title).toSet();
          final newTitles = res.articles.map((a) => a.title).toSet();
          if (newTitles.difference(oldTitles).isEmpty) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('No newer articles found.')),
            );
          }
        }
        setState(() {
          _newsResponse = res;
          _lastFetchTime = DateTime.now();
          _isFetchingNews = false;
        });
      }
    } catch (e) {
      // Fallback to cache
      try {
        final cache = await StorageService.getCachedNews();
        if (cache != null && mounted) {
          setState(() {
            _newsResponse = cache['news'] as NewsResponse;
            _newsError = 'CACHED — LAST UPDATED: ${cache['timestamp'].toString().split('.').first}';
            _lastFetchTime = cache['timestamp'] as DateTime;
            _isFetchingNews = false;
          });
          return;
        }
      } catch (_) {}

      if (mounted) {
        setState(() {
          _newsError = 'No cached news available offline.';
          _isFetchingNews = false;
        });
      }
    }
  }

  Future<void> _checkServerStatus() async {
    final ok = await _apiService.checkHealth();
    if (mounted) {
      setState(() {
        _isServerConnected = ok;
        _isCheckingHealth = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: AppColors.primary,
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.shield_outlined, color: Colors.white, size: 20),
            ),
            const SizedBox(width: 10),
            const Text(
              AppStrings.appName,
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 20),
            ),
          ],
        ),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16.0),
            child: Row(
              children: [
                Container(
                  width: 10,
                  height: 10,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: _isCheckingHealth
                        ? Colors.amber
                        : _isServerConnected
                            ? AppColors.verdictGenuine
                            : AppColors.verdictMisleading,
                  ),
                ),
                const SizedBox(width: 6),
                Text(
                  _isCheckingHealth
                      ? 'Connecting...'
                      : _isServerConnected
                          ? 'API Online'
                          : 'API Offline',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                    color: isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => _fetchNews(forceRefresh: true),
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Hero Banner
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(20.0),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: isDark
                      ? [const Color(0xFF1E3A8A), const Color(0xFF0F172A)]
                      : [const Color(0xFF1E3A8A), const Color(0xFF2563EB)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'TruthLens',
                    style: TextStyle(
                      color: Colors.white70,
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      letterSpacing: 1.0,
                    ),
                  ),
                  const SizedBox(height: 6),
                  const Text(
                    'Check before you share.',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Analyze suspect headlines, viral forwards, or article claims using evidence-based detection.',
                    style: TextStyle(color: Colors.white, fontSize: 13, height: 1.4),
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton.icon(
                    onPressed: widget.onCheckNewsPressed,
                    icon: const Icon(Icons.search, size: 18),
                    label: const Text('Check a News Article'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.white,
                      foregroundColor: AppColors.primary,
                      elevation: 0,
                      minimumSize: const Size(180, 44),
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // Misinformation Literacy Section
            Text(
              'Evidence & Misinformation Guide',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: isDark ? AppColors.textPrimaryDark : AppColors.textPrimaryLight,
              ),
            ),
            const SizedBox(height: 12),
            _buildLiteracyCard(
              icon: Icons.lightbulb_outline,
              title: 'Spotting Sensational Language',
              description:
                  'Misleading forwards frequently use excessive capitalization, multiple exclamation marks, and urgent demands like "FORWARD TO ALL".',
              isDark: isDark,
            ),
            const SizedBox(height: 10),
            _buildLiteracyCard(
              icon: Icons.account_balance_outlined,
              title: 'Source Transparency',
              description:
                  'Always check if an article names primary sources, authors, and dates, or if it makes claims attributed only to "unnamed scientists".',
              isDark: isDark,
            ),

            const SizedBox(height: 24),
            TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: 'Search news...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: IconButton(
                  icon: const Icon(Icons.clear),
                  onPressed: () {
                    _searchController.clear();
                    _fetchNews(forceRefresh: true);
                  },
                ),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                contentPadding: const EdgeInsets.symmetric(horizontal: 16),
              ),
              onSubmitted: (_) => _fetchNews(forceRefresh: true),
            ),
            const SizedBox(height: 12),
            SizedBox(
              height: 40,
              child: ListView.builder(
                scrollDirection: Axis.horizontal,
                itemCount: _categories.length,
                itemBuilder: (context, index) {
                  final cat = _categories[index];
                  final isSelected = cat == _selectedCategory;
                  return Padding(
                    padding: const EdgeInsets.only(right: 8.0),
                    child: ChoiceChip(
                      label: Text(cat),
                      selected: isSelected,
                      onSelected: (selected) {
                        if (selected) {
                          setState(() => _selectedCategory = cat);
                          _fetchNews(forceRefresh: true);
                        }
                      },
                    ),
                  );
                },
              ),
            ),
            const SizedBox(height: 24),

            // Latest Public Dispatches (Live News)
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Live News Feed',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: isDark ? AppColors.textPrimaryDark : AppColors.textPrimaryLight,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'News from selected public sources',
                      style: TextStyle(
                        fontSize: 12,
                        color: isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight,
                      ),
                    ),
                    if (_lastFetchTime != null) ...[
                      const SizedBox(height: 4),
                      Text(
                        'Last updated: ${_lastFetchTime!.toLocal().toString().split('.')[0]}',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w500,
                          color: isDark ? Colors.amber[200] : Colors.amber[800],
                        ),
                      ),
                    ],
                  ],
                ),
                IconButton(
                  icon: const Icon(Icons.refresh, size: 20),
                  onPressed: () => _fetchNews(forceRefresh: true),
                  tooltip: 'Refresh News',
                ),
              ],
            ),
            const SizedBox(height: 12),
            
            if (_isFetchingNews)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(24.0),
                  child: CircularProgressIndicator(),
                ),
              )
            else if (_newsError != null && _newsError!.startsWith('CACHED'))
              Column(
                children: [
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.symmetric(vertical: 8),
                    margin: const EdgeInsets.only(bottom: 12),
                    decoration: BoxDecoration(
                      color: Colors.amber.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      _newsError!,
                      textAlign: TextAlign.center,
                      style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.amber),
                    ),
                  ),
                  if (_newsResponse != null && _newsResponse!.articles.isNotEmpty)
                    ..._newsResponse!.articles.map((article) => _buildDynamicFeedCard(article, isDark)).toList(),
                ],
              )
            else if (_newsError != null)
              Center(
                child: Padding(
                  padding: const EdgeInsets.all(24.0),
                  child: Column(
                    children: [
                      const Icon(Icons.cloud_off, color: Colors.red, size: 36),
                      const SizedBox(height: 8),
                      Text(_newsError!, style: TextStyle(color: isDark ? Colors.white : Colors.black)),
                      const SizedBox(height: 8),
                      ElevatedButton(
                        onPressed: () => _fetchNews(forceRefresh: true),
                        child: const Text('Retry'),
                      )
                    ],
                  ),
                ),
              )
            else if (_newsResponse == null || _newsResponse!.articles.isEmpty)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(24.0),
                  child: Text('No current news is available.'),
                ),
              )
            else
              ..._newsResponse!.articles.map((article) => _buildDynamicFeedCard(article, isDark)).toList(),
          ],
        ),
      ),
      ),
    );
  }

  Widget _buildDynamicFeedCard(NewsArticle article, bool isDark) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(14.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Source: ${article.sourceName}',
                  style: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: AppColors.primaryLight,
                  ),
                ),
                Text(
                  _formatDate(article.publishedAt),
                  style: TextStyle(
                    fontSize: 11,
                    color: isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              article.title,
              style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, height: 1.3),
            ),
            if (article.description.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(
                article.description,
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  fontSize: 12,
                  height: 1.4,
                  color: isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight,
                ),
              ),
            ],
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton.icon(
                  onPressed: () async {
                    final url = Uri.parse(article.url);
                    if (await canLaunchUrl(url)) {
                      await launchUrl(url, mode: LaunchMode.externalApplication);
                    }
                  },
                  icon: const Icon(Icons.open_in_browser, size: 14),
                  label: const Text('Open Article', style: TextStyle(fontSize: 12)),
                  style: TextButton.styleFrom(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    minimumSize: Size.zero,
                  ),
                ),
                const SizedBox(width: 8),
                TextButton.icon(
                  onPressed: () {
                    // Send headline + description as text to be checked
                    final textToCheck = '${article.title}\n\n${article.description}';
                    widget.onCheckText(textToCheck);
                  },
                  icon: const Icon(Icons.check, size: 14),
                  label: const Text('Check This News', style: TextStyle(fontSize: 12)),
                  style: TextButton.styleFrom(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    minimumSize: Size.zero,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  String _formatDate(String isoString) {
    try {
      final dt = DateTime.parse(isoString).toLocal();
      final now = DateTime.now();
      final diff = now.difference(dt);
      if (diff.inMinutes < 60) {
        return '${diff.inMinutes}m ago';
      } else if (diff.inHours < 24) {
        return '${diff.inHours}h ago';
      } else {
        return '${dt.year}-${dt.month.toString().padLeft(2, '0')}-${dt.day.toString().padLeft(2, '0')}';
      }
    } catch (_) {
      return 'Recent';
    }
  }

  Widget _buildLiteracyCard({
    required IconData icon,
    required String title,
    required String description,
    required bool isDark,
  }) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14.0),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: isDark ? const Color(0xFF334155) : const Color(0xFFF1F5F9),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(icon, size: 20, color: AppColors.primaryLight),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    description,
                    style: TextStyle(
                      fontSize: 12,
                      height: 1.4,
                      color: isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFeedCard({
    required String title,
    required String source,
    required String time,
    required bool isDark,
  }) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  source,
                  style: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: AppColors.primaryLight,
                  ),
                ),
                Text(
                  time,
                  style: TextStyle(
                    fontSize: 11,
                    color: isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              title,
              style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, height: 1.3),
            ),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: isDark ? const Color(0xFF334155) : const Color(0xFFF1F5F9),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Text(
                    'Credibility: Pending Check',
                    style: TextStyle(
                      fontSize: 11,
                      color: isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
                TextButton.icon(
                  onPressed: widget.onCheckNewsPressed,
                  icon: const Icon(Icons.check, size: 14),
                  label: const Text('Check Article', style: TextStyle(fontSize: 12)),
                  style: TextButton.styleFrom(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    minimumSize: Size.zero,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
