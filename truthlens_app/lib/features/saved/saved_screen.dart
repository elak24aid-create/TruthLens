import 'package:flutter/material.dart';
import '../../services/saved_service.dart';
import '../checker/result_screen.dart';

class SavedScreen extends StatefulWidget {
  const SavedScreen({Key? key}) : super(key: key);

  @override
  _SavedScreenState createState() => _SavedScreenState();
}

class _SavedScreenState extends State<SavedScreen> {
  final SavedService _savedService = SavedService();
  List<SavedResult> _savedResults = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadSaved();
  }

  Future<void> _loadSaved() async {
    final results = await _savedService.getSavedResults();
    setState(() {
      _savedResults = results;
      _isLoading = false;
    });
  }

  Future<void> _clearSaved() async {
    await _savedService.clearSaved();
    _loadSaved();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Saved Results'),
        actions: [
          IconButton(
            icon: const Icon(Icons.delete_outline),
            onPressed: _clearSaved,
            tooltip: 'Clear All',
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _savedResults.isEmpty
              ? const Center(child: Text('No saved results.'))
              : ListView.builder(
                  itemCount: _savedResults.length,
                  itemBuilder: (context, index) {
                    final item = _savedResults[index];
                    return Card(
                      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                      child: ListTile(
                        title: Text(item.claim, maxLines: 2, overflow: TextOverflow.ellipsis),
                        subtitle: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(item.date),
                            if (item.note != null && item.note!.isNotEmpty)
                              Text('Note: ${item.note}', style: const TextStyle(fontStyle: FontStyle.italic)),
                          ],
                        ),
                        onTap: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (_) => ResultScreen(
                                result: item.result,
                                originalText: item.claim,
                              ),
                            ),
                          );
                        },
                      ),
                    );
                  },
                ),
    );
  }
}
