import 'package:flutter/material.dart';
import '../../models/history_item.dart';
import '../../models/verdict.dart';
import '../../services/api_service.dart';
import '../../services/local_history_service.dart';
import '../../widgets/verdict_badge.dart';
import '../checker/result_screen.dart';
import '../../core/constants/app_colors.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  final ApiService _apiService = ApiService();
  final LocalHistoryService _localHistoryService = LocalHistoryService();

  List<HistoryItem> _items = [];
  bool _isLoading = true;
  String _searchQuery = '';
  VerdictType? _selectedFilter;
  String? _selectedInputFilter;

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  Future<void> _loadHistory() async {
    setState(() {
      _isLoading = true;
    });

    // Try fetching from backend first
    List<HistoryItem> fetched = await _apiService.fetchHistory();
    // If backend has no history, fallback to local storage
    if (fetched.isEmpty) {
      fetched = await _localHistoryService.getLocalHistory();
    }

    if (mounted) {
      setState(() {
        _items = fetched;
        _isLoading = false;
      });
    }
  }

  Future<void> _deleteItem(String id) async {
    await _apiService.deleteHistory(id);
    await _localHistoryService.deleteLocalItem(id);
    setState(() {
      _items.removeWhere((i) => i.id == id);
    });
  }

  Future<void> _clearAll() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Clear All History?'),
        content: const Text('This will delete all saved check records. This action cannot be undone.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: TextButton.styleFrom(foregroundColor: AppColors.verdictMisleading),
            child: const Text('Clear All'),
          ),
        ],
      ),
    );

    if (confirm == true) {
      await _apiService.clearAllHistory();
      await _localHistoryService.clearLocalHistory();
      setState(() {
        _items.clear();
      });
    }
  }

  List<HistoryItem> get _filteredItems {
    return _items.where((item) {
      final title = item.analysisResult?.extractedMetadata?['title']?.toString() ?? '';
      final source = item.analysisResult?.extractedMetadata?['source_name']?.toString() ?? '';
      
      final matchesSearch = _searchQuery.isEmpty ||
          item.textSnippet.toLowerCase().contains(_searchQuery.toLowerCase()) ||
          item.summary.toLowerCase().contains(_searchQuery.toLowerCase()) ||
          title.toLowerCase().contains(_searchQuery.toLowerCase()) ||
          source.toLowerCase().contains(_searchQuery.toLowerCase());
          
      final matchesVerdict = _selectedFilter == null || item.verdict == _selectedFilter;
      final matchesInput = _selectedInputFilter == null || item.inputType == _selectedInputFilter;
      return matchesSearch && matchesVerdict && matchesInput;
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final displayItems = _filteredItems;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Check History', style: TextStyle(fontWeight: FontWeight.bold)),
        actions: [
          if (_items.isNotEmpty)
            IconButton(
              icon: const Icon(Icons.delete_sweep_outlined),
              tooltip: 'Clear All History',
              onPressed: _clearAll,
            ),
        ],
      ),
      body: Column(
        children: [
          // Search & Filters Header
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              children: [
                TextField(
                  decoration: InputDecoration(
                    hintText: 'Search past checks...',
                    prefixIcon: const Icon(Icons.search, size: 20),
                    filled: true,
                    fillColor: isDark ? const Color(0xFF1E293B) : const Color(0xFFF1F5F9),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide.none,
                    ),
                    contentPadding: const EdgeInsets.symmetric(vertical: 0, horizontal: 16),
                  ),
                  onChanged: (val) {
                    setState(() {
                      _searchQuery = val;
                    });
                  },
                ),
                const SizedBox(height: 10),
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Row(
                    children: [
                      FilterChip(
                        label: const Text('All Inputs'),
                        selected: _selectedInputFilter == null,
                        onSelected: (_) {
                          setState(() {
                            _selectedInputFilter = null;
                          });
                        },
                      ),
                      const SizedBox(width: 8),
                      FilterChip(
                        label: const Text('Text'),
                        selected: _selectedInputFilter == 'text',
                        onSelected: (selected) {
                          setState(() {
                            _selectedInputFilter = selected ? 'text' : null;
                          });
                        },
                      ),
                      const SizedBox(width: 8),
                      FilterChip(
                        label: const Text('URL'),
                        selected: _selectedInputFilter == 'url',
                        onSelected: (selected) {
                          setState(() {
                            _selectedInputFilter = selected ? 'url' : null;
                          });
                        },
                      ),
                      const SizedBox(width: 8),
                      FilterChip(
                        label: const Text('Image'),
                        selected: _selectedInputFilter == 'image',
                        onSelected: (selected) {
                          setState(() {
                            _selectedInputFilter = selected ? 'image' : null;
                          });
                        },
                      ),
                      const SizedBox(width: 8),
                      FilterChip(
                        label: const Text('Video'),
                        selected: _selectedInputFilter == 'video',
                        onSelected: (selected) {
                          setState(() {
                            _selectedInputFilter = selected ? 'video' : null;
                          });
                        },
                      ),
                      const SizedBox(width: 8),
                      FilterChip(
                        label: const Text('News'),
                        selected: _selectedInputFilter == 'news',
                        onSelected: (selected) {
                          setState(() {
                            _selectedInputFilter = selected ? 'news' : null;
                          });
                        },
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 10),
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Row(
                    children: [
                      FilterChip(
                        label: const Text('All Verdicts'),
                        selected: _selectedFilter == null,
                        onSelected: (_) {
                          setState(() {
                            _selectedFilter = null;
                          });
                        },
                      ),
                      const SizedBox(width: 8),
                      FilterChip(
                        label: const Text('Misleading'),
                        selected: _selectedFilter == VerdictType.likelyMisleading,
                        onSelected: (selected) {
                          setState(() {
                            _selectedFilter = selected ? VerdictType.likelyMisleading : null;
                          });
                        },
                      ),
                      const SizedBox(width: 8),
                      FilterChip(
                        label: const Text('Genuine'),
                        selected: _selectedFilter == VerdictType.likelyGenuine,
                        onSelected: (selected) {
                          setState(() {
                            _selectedFilter = selected ? VerdictType.likelyGenuine : null;
                          });
                        },
                      ),
                      const SizedBox(width: 8),
                      FilterChip(
                        label: const Text('Unverified'),
                        selected: _selectedFilter == VerdictType.unverified,
                        onSelected: (selected) {
                          setState(() {
                            _selectedFilter = selected ? VerdictType.unverified : null;
                          });
                        },
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // Items List / States
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : displayItems.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(
                              Icons.history_toggle_off,
                              size: 48,
                              color: isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight,
                            ),
                            const SizedBox(height: 12),
                            Text(
                              _items.isEmpty ? 'No Checks Saved Yet' : 'No Matching Checks Found',
                              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                            ),
                            const SizedBox(height: 6),
                            Text(
                              _items.isEmpty
                                  ? 'Analyses you save from the Check News screen will appear here.'
                                  : 'Try adjusting your search query or filter tags.',
                              style: TextStyle(
                                fontSize: 13,
                                color: isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight,
                              ),
                            ),
                          ],
                        ),
                      )
                    : RefreshIndicator(
                        onRefresh: _loadHistory,
                        child: ListView.builder(
                          padding: const EdgeInsets.symmetric(horizontal: 16),
                          itemCount: displayItems.length,
                          itemBuilder: (context, index) {
                            final item = displayItems[index];
                            return Dismissible(
                              key: Key(item.id),
                              direction: DismissDirection.endToStart,
                              background: Container(
                                alignment: Alignment.centerRight,
                                padding: const EdgeInsets.only(right: 20),
                                decoration: BoxDecoration(
                                  color: AppColors.verdictMisleading,
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: const Icon(Icons.delete_outline, color: Colors.white),
                              ),
                              onDismissed: (_) => _deleteItem(item.id),
                              child: Card(
                                margin: const EdgeInsets.only(bottom: 12),
                                clipBehavior: Clip.antiAlias,
                                child: InkWell(
                                  onTap: () {
                                    if (item.analysisResult != null) {
                                      Navigator.push(
                                        context,
                                        MaterialPageRoute(
                                          builder: (_) => ResultScreen(
                                            result: item.analysisResult!,
                                            originalText: item.textSnippet,
                                            inputType: item.inputType,
                                            isHistory: true,
                                            historyTimestamp: item.timestamp,
                                          ),
                                        ),
                                      );
                                    } else {
                                      ScaffoldMessenger.of(context).showSnackBar(
                                        const SnackBar(content: Text('Detailed result not available for this legacy check.')),
                                      );
                                    }
                                  },
                                  child: Padding(
                                    padding: const EdgeInsets.all(14.0),
                                    child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Row(
                                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                        children: [
                                          Row(
                                            children: [
                                              Icon(
                                                item.inputType == 'video' ? Icons.video_library
                                                : item.inputType == 'image' ? Icons.image
                                                : item.inputType == 'url' ? Icons.link
                                                : item.inputType == 'news' ? Icons.article
                                                : Icons.text_snippet,
                                                size: 18,
                                                color: isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight,
                                              ),
                                              const SizedBox(width: 8),
                                              VerdictBadge(verdict: item.verdict),
                                            ],
                                          ),
                                          Text(
                                            'Score: ${item.confidence}%',
                                            style: TextStyle(
                                              fontSize: 12,
                                              fontWeight: FontWeight.w600,
                                              color: isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight,
                                            ),
                                          ),
                                        ],
                                      ),
                                      const SizedBox(height: 10),
                                      Text(
                                        item.textSnippet,
                                        maxLines: 2,
                                        overflow: TextOverflow.ellipsis,
                                        style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
                                      ),
                                      const SizedBox(height: 6),
                                      Text(
                                        item.summary,
                                        maxLines: 2,
                                        overflow: TextOverflow.ellipsis,
                                        style: TextStyle(
                                          fontSize: 12,
                                          color: isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight,
                                        ),
                                      ),
                                      const SizedBox(height: 10),
                                      Row(
                                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                        children: [
                                          Text(
                                            item.timestamp.length >= 10
                                                ? item.timestamp.substring(0, 10)
                                                : 'Recent',
                                            style: TextStyle(
                                              fontSize: 11,
                                              color: isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight,
                                            ),
                                          ),
                                          IconButton(
                                            icon: const Icon(Icons.delete_outline, size: 18),
                                            tooltip: 'Delete Check',
                                            onPressed: () => _deleteItem(item.id),
                                          ),
                                        ],
                                      ),
                                    ],
                                  ),
                                  ),
                                ),
                              ),
                            );
                          },
                        ),
                      ),
          ),
        ],
      ),
    );
  }
}
