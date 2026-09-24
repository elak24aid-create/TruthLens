import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:typed_data';
import 'package:image_picker/image_picker.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_strings.dart';
import '../../services/api_service.dart';
import '../../widgets/skeleton_loader.dart';
import 'result_screen.dart';

class CheckerScreen extends StatefulWidget {
  final String? initialText;
  const CheckerScreen({super.key, this.initialText});

  @override
  State<CheckerScreen> createState() => _CheckerScreenState();
}

class _CheckerScreenState extends State<CheckerScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final TextEditingController _textController = TextEditingController();
  final TextEditingController _urlController = TextEditingController();
  final ApiService _apiService = ApiService();

  bool _isLoading = false;
  String? _errorMessage;
  
  XFile? _selectedImage;
  Uint8List? _imageBytes;
  XFile? _selectedVideo;
  Uint8List? _videoBytes;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _tabController.addListener(() {
      if (_tabController.indexIsChanging) {
        setState(() {
          _errorMessage = null;
        });
      }
    });
    if (widget.initialText != null && widget.initialText!.isNotEmpty) {
      _textController.text = widget.initialText!;
    }
  }

  @override
  void didUpdateWidget(CheckerScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.initialText != oldWidget.initialText && widget.initialText != null && widget.initialText!.isNotEmpty) {
      _textController.text = widget.initialText!;
      _tabController.animateTo(0);
    }
  }

  @override
  void dispose() {
    _tabController.dispose();
    _textController.dispose();
    _urlController.dispose();
    super.dispose();
  }

  Future<void> _pasteFromClipboard() async {
    final data = await Clipboard.getData(Clipboard.kTextPlain);
    if (data?.text != null) {
      setState(() {
        _textController.text = data!.text!;
        _errorMessage = null;
      });
    }
  }

  void _loadSample(String sample) {
    setState(() {
      _textController.text = sample;
      _errorMessage = null;
    });
  }

  Future<void> _analyzeNewsText() async {
    final text = _textController.text.trim();
    if (text.length < 10) {
      setState(() {
        _errorMessage = 'Please enter at least 10 characters to analyze.';
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final result = await _apiService.checkText(text);
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => ResultScreen(
              result: result,
              originalText: text,
              inputType: 'text',
            ),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
          _errorMessage = e.toString();
        });
      }
    }
  }

  Future<void> _analyzeUrl() async {
    final url = _urlController.text.trim();
    if (url.isEmpty || !url.startsWith(RegExp(r'http(s)?://'))) {
      setState(() {
        _errorMessage = 'Please enter a valid HTTP or HTTPS URL.';
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final urlData = await _apiService.checkUrl(url);
      final claimText = urlData['claim_text'] as String;
      
      // Use the extracted claim text to perform the ML analysis
      final result = await _apiService.checkText(claimText);
      
      // Pass the extracted metadata to ResultScreen
      // Since we cannot easily inject it into AnalysisResult model if it's strictly typed without modifying the model,
      // Actually, AnalysisResult has extractedMetadata!
      // The checkText backend currently doesn't know about the URL. 
      // We'll modify the Dart AnalysisResult object before navigating.
      result.extractedMetadata = urlData;

      if (mounted) {
        setState(() {
          _isLoading = false;
        });
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => ResultScreen(
              result: result,
              originalText: url,
              inputType: 'url',
            ),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
          _errorMessage = e.toString();
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Check News', style: TextStyle(fontWeight: FontWeight.bold)),
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: AppColors.primaryLight,
          labelColor: AppColors.primaryLight,
          unselectedLabelColor: isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight,
          tabs: const [
            Tab(icon: Icon(Icons.article_outlined, size: 20), text: 'Text / Headline'),
            Tab(icon: Icon(Icons.link_outlined, size: 20), text: 'Article URL'), Tab(icon: Icon(Icons.image_outlined, size: 20), text: 'Image'),
            Tab(icon: Icon(Icons.video_library_outlined, size: 20), text: 'Video'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          // Tab 1: Text Checker
          _buildTextTab(isDark),
          // Tab 2: URL Checker
          _buildUrlTab(isDark), _buildImageTab(isDark),
                  _buildVideoTab(isDark),
        ],
      ),
    );
  }

  Widget _buildTextTab(bool isDark) {
    if (_isLoading) {
      return Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Analyzing News Signals...',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              'Running language detection, stylistic extraction, and multi-signal verification.',
              style: TextStyle(
                fontSize: 12,
                color: isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight,
              ),
            ),
            const SizedBox(height: 24),
            const SkeletonLoader(height: 120, borderRadius: 16),
            const SizedBox(height: 16),
            const SkeletonLoader(height: 80, borderRadius: 12),
            const SizedBox(height: 16),
            const SkeletonLoader(height: 60, borderRadius: 12),
          ],
        ),
      );
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Paste News Content',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: isDark ? AppColors.textPrimaryDark : AppColors.textPrimaryLight,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'Paste an article body, headline, or social media forwarded message.',
            style: TextStyle(
              fontSize: 13,
              color: isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight,
            ),
          ),
          const SizedBox(height: 12),

          // Input Card
          Card(
            child: Padding(
              padding: const EdgeInsets.all(12.0),
              child: Column(
                children: [
                  TextField(
                    controller: _textController,
                    maxLines: 7,
                    decoration: const InputDecoration(
                      hintText: AppStrings.textPlaceholder,
                      border: InputBorder.none,
                      hintStyle: TextStyle(fontSize: 13),
                    ),
                    onChanged: (_) {
                      if (_errorMessage != null) {
                        setState(() {
                          _errorMessage = null;
                        });
                      }
                    },
                  ),
                  const Divider(height: 1),
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      TextButton.icon(
                        onPressed: _pasteFromClipboard,
                        icon: const Icon(Icons.paste_rounded, size: 16),
                        label: const Text('Paste', style: TextStyle(fontSize: 12)),
                      ),
                      if (_textController.text.isNotEmpty)
                        TextButton(
                          onPressed: () {
                            setState(() {
                              _textController.clear();
                              _errorMessage = null;
                            });
                          },
                          child: const Text('Clear', style: TextStyle(fontSize: 12)),
                        ),
                    ],
                  ),
                ],
              ),
            ),
          ),

          if (_errorMessage != null) ...[
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppColors.verdictMisleadingBg,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: AppColors.verdictMisleading.withOpacity(0.3)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.error_outline, size: 18, color: AppColors.verdictMisleading),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      _errorMessage!,
                      style: const TextStyle(
                        fontSize: 12,
                        color: AppColors.verdictMisleading,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],

          const SizedBox(height: 16),

          // Quick Test Samples
          Text(
            'Quick Test Examples:',
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight,
            ),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            children: [
              ActionChip(
                label: const Text('Sensational Claim', style: TextStyle(fontSize: 11)),
                onPressed: () => _loadSample(
                  'URGENT WARNING! SHOCKING MIRACLE CURE THEY DON\'T WANT YOU TO KNOW! DRINK LEMON JUICE TO CURE ALL ILLNESSES 100% GUARANTEED! FORWARD TO ALL!',
                ),
              ),
              ActionChip(
                label: const Text('Standard Wire Report', style: TextStyle(fontSize: 11)),
                onPressed: () => _loadSample(
                  'Reuters reports that international meteorological teams observed a 1.2 degree shift in seasonal rainfall patterns across agricultural regions.',
                ),
              ),
            ],
          ),

          const SizedBox(height: 24),

          // Analyze Button
          ElevatedButton.icon(
            onPressed: _analyzeNewsText,
            icon: const Icon(Icons.travel_explore_rounded, size: 20),
            label: const Text(AppStrings.analyzeButton),
          ),
        ],
      ),
    );
  }

  
  Widget _buildUrlTab(bool isDark) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Inspect Article by URL',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: isDark ? AppColors.textPrimaryDark : AppColors.textPrimaryLight,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'Enter the web link to a published news piece.',
            style: TextStyle(
              fontSize: 13,
              color: isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight,
            ),
          ),
          const SizedBox(height: 16),
          Card(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 14.0, vertical: 6.0),
              child: TextField(
                controller: _urlController,
                decoration: const InputDecoration(
                  hintText: AppStrings.urlPlaceholder,
                  border: InputBorder.none,
                  icon: Icon(Icons.link, size: 20),
                ),
              ),
            ),
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: isDark ? const Color(0xFF1E293B) : const Color(0xFFF1F5F9),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              children: [
                const Icon(Icons.info_outline, size: 16, color: AppColors.primaryLight),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Tip: If a website is paywalled or blocks automated crawlers, copy and paste the article text into the Text tab for immediate analysis.',
                    style: TextStyle(
                      fontSize: 12,
                      color: isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight,
                    ),
                  ),
                ),
              ],
            ),
          ),
          
          if (_errorMessage != null && _tabController.index == 1) ...[
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppColors.verdictMisleadingBg,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: AppColors.verdictMisleading.withAlpha(76)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.error_outline, size: 18, color: AppColors.verdictMisleading),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      _errorMessage!,
                      style: const TextStyle(
                        fontSize: 12,
                        color: AppColors.verdictMisleading,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
          
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: _analyzeUrl,
            icon: const Icon(Icons.search, size: 20),
            label: const Text('Analyze URL'),
          ),
        ],
      ),
    );
  }

  Widget _buildImageTab(bool isDark) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Upload a news screenshot or image',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: isDark ? AppColors.textPrimaryDark : AppColors.textPrimaryLight,
            ),
          ),
          const SizedBox(height: 16),
          if (_imageBytes != null)
            Expanded(
              child: Column(
                children: [
                  Expanded(
                    child: Image.memory(
                      _imageBytes!,
                      fit: BoxFit.contain,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'Selected: ${_selectedImage?.name}',
                    style: const TextStyle(fontSize: 12),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      TextButton.icon(
                        onPressed: _pickImage,
                        icon: const Icon(Icons.refresh),
                        label: const Text('Change Image'),
                      ),
                      const SizedBox(width: 16),
                      ElevatedButton.icon(
                        onPressed: _analyzeImage,
                        icon: const Icon(Icons.search),
                        label: const Text('Check Image'),
                      ),
                    ],
                  ),
                ],
              ),
            )
          else
            Expanded(
              child: Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.image, size: 64, color: Colors.grey),
                    const SizedBox(height: 16),
                    ElevatedButton.icon(
                      onPressed: _pickImage,
                      icon: const Icon(Icons.upload_file),
                      label: const Text('Select Image'),
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }

  Future<void> _pickImage() async {
    final picker = ImagePicker();
    try {
      final pickedFile = await picker.pickImage(source: ImageSource.gallery);
      if (pickedFile != null) {
        final bytes = await pickedFile.readAsBytes();
        setState(() {
          _selectedImage = pickedFile;
          _imageBytes = bytes;
          _errorMessage = null;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to pick image: $e';
      });
    }
  }

  Future<void> _analyzeImage() async {
    if (_imageBytes == null) {
      setState(() {
        _errorMessage = 'Please select an image first.';
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final imgData = await _apiService.checkImage(
        _imageBytes!.toList(),
        _selectedImage?.name ?? 'image.png',
      );
      final claimText = imgData['claim_text'] as String;
      
      final result = await _apiService.checkText(claimText);
      result.extractedMetadata = imgData;

      if (mounted) {
        setState(() {
          _isLoading = false;
        });
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => ResultScreen(
              result: result,
              originalText: _selectedImage?.name ?? 'Image',
              inputType: 'image',
            ),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
          _errorMessage = e.toString();
        });
      }
    }
  }

  Widget _buildVideoTab(bool isDark) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Upload a news video',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: isDark ? AppColors.textPrimaryDark : AppColors.textPrimaryLight,
            ),
          ),
          const SizedBox(height: 16),
          if (_selectedVideo != null)
            Expanded(
              child: Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.video_file, size: 64, color: AppColors.primaryLight),
                    const SizedBox(height: 12),
                    Text(
                      'Selected: ${_selectedVideo?.name}',
                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                      textAlign: TextAlign.center,
                    ),
                    if (_videoBytes != null)
                      Text(
                        'Size: ${(_videoBytes!.length / (1024 * 1024)).toStringAsFixed(2)} MB',
                        style: const TextStyle(fontSize: 11),
                      ),
                    const SizedBox(height: 24),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        TextButton.icon(
                          onPressed: _pickVideo,
                          icon: const Icon(Icons.refresh),
                          label: const Text('Change Video'),
                        ),
                        const SizedBox(width: 16),
                        ElevatedButton.icon(
                          onPressed: _analyzeVideo,
                          icon: const Icon(Icons.search),
                          label: const Text('Check Video'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            )
          else
            Expanded(
              child: Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.video_library, size: 64, color: Colors.grey),
                    const SizedBox(height: 16),
                    ElevatedButton.icon(
                      onPressed: _pickVideo,
                      icon: const Icon(Icons.upload_file),
                      label: const Text('Select Video (Max 50MB)'),
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }

  Future<void> _pickVideo() async {
    final picker = ImagePicker();
    try {
      final pickedFile = await picker.pickVideo(source: ImageSource.gallery);
      if (pickedFile != null) {
        final bytes = await pickedFile.readAsBytes();
        setState(() {
          _selectedVideo = pickedFile;
          _videoBytes = bytes;
          _errorMessage = null;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to pick video: $e';
      });
    }
  }

  Future<void> _analyzeVideo() async {
    if (_videoBytes == null) {
      setState(() {
        _errorMessage = 'Please select a video first.';
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final vidData = await _apiService.checkVideo(
        _videoBytes!.toList(),
        _selectedVideo?.name ?? 'video.mp4',
      );
      final claimText = vidData['claim_text'] as String;
      
      final result = await _apiService.checkText(claimText);
      result.extractedMetadata = vidData;

      if (mounted) {
        setState(() {
          _isLoading = false;
        });
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => ResultScreen(
              result: result,
              originalText: _selectedVideo?.name ?? 'Video',
              inputType: 'video',
            ),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
          _errorMessage = e.toString();
        });
      }
    }
  }
}
