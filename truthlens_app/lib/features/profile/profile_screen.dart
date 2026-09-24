import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../config/theme_config.dart';
import '../../config/api_config.dart';
import '../../core/constants/app_strings.dart';
import '../../services/storage_service.dart';
import '../auth/splash_screen.dart';

class ProfileScreen extends StatefulWidget {
  final ThemeMode currentThemeMode;
  final ValueChanged<ThemeMode>? onThemeModeChanged;

  const ProfileScreen({
    super.key,
    this.currentThemeMode = ThemeMode.system,
    this.onThemeModeChanged,
  });

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  String _selectedLanguage = 'English';
  Map<String, String>? _user;

  @override
  void initState() {
    super.initState();
    _loadUser();
  }

  void _loadUser() async {
    final user = await StorageService.getUser();
    if (mounted) {
      setState(() {
        _user = user;
      });
    }
  }

  void _logout() async {
    await StorageService.logout();
    if (!mounted) return;
    Navigator.of(context, rootNavigator: true).pushReplacement(
      MaterialPageRoute(
        builder: (_) => SplashScreen(
          currentThemeMode: widget.currentThemeMode,
          onThemeModeChanged: widget.onThemeModeChanged ?? (mode) {},
        ),
      ),
    );
  }

  void _showLanguageDialog() {
    showDialog(
      context: context,
      builder: (ctx) => SimpleDialog(
        title: const Text('Select Analysis Language'),
        children: [
          'English',
          'Tamil',
          'Hindi',
          'Telugu',
          'Malayalam',
          'Kannada',
          'Bengali',
          'Spanish',
          'French',
          'Arabic',
        ].map((lang) {
          return SimpleDialogOption(
            onPressed: () {
              setState(() {
                _selectedLanguage = lang;
              });
              Navigator.pop(ctx);
            },
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 6.0),
              child: Text(lang, style: const TextStyle(fontSize: 15)),
            ),
          );
        }).toList(),
      ),
    );
  }

  void _showAiLimitationsDialog() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('AI Limitations & Ethics'),
        content: const SingleChildScrollView(
          child: Text(
            'TruthLens is an AI-assisted research and verification tool.\n\n'
            'Important Disclosures:\n'
            '• TruthLens DOES NOT claim to possess absolute truth.\n'
            '• The confidence score reflects statistical and heuristic signal consistency, not certified factual reality.\n'
            '• Statistical models may misclassify complex sarcasm, highly novel breaking developments, or niche localized contexts.\n'
            '• Users must cross-examine critical claims with accredited official news agencies and official government gazettes before making decisions.',
            style: TextStyle(fontSize: 13, height: 1.5),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Understood'),
          ),
        ],
      ),
    );
  }

  void _showAboutDialog() {
    showAboutDialog(
      context: context,
      applicationName: AppStrings.appName,
      applicationVersion: 'Final Release (v1.0.0)',
      applicationLegalese: 'Designed for college major project demonstration.',
      children: const [
        SizedBox(height: 12),
        Text(
          'TruthLens integrates scikit-learn statistical natural language processing, '
          'defensive text preprocessing, linguistic heuristics, and verifiable source assessments '
          'to combat digital disinformation.',
          style: TextStyle(fontSize: 13),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final userName = _user?['name'] ?? 'Guest User';
    final userEmail = _user?['email'] ?? 'Not logged in';

    return Scaffold(
      appBar: AppBar(
        title: const Text('Profile & Settings', style: TextStyle(fontWeight: FontWeight.bold)),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16.0),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Row(
                children: [
                  CircleAvatar(
                    radius: 28,
                    backgroundColor: Theme.of(context).colorScheme.primaryContainer,
                    child: Icon(Icons.person, size: 32, color: Theme.of(context).colorScheme.onPrimaryContainer),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          userName,
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          userEmail,
                          style: TextStyle(
                            fontSize: 12,
                            color: isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight,
                          ),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.logout),
                    onPressed: _logout,
                    tooltip: 'Logout',
                  )
                ],
              ),
            ),
          ),

          const SizedBox(height: 20),

          // Preferences Section
          Text(
            'Preferences',
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight,
            ),
          ),
          const SizedBox(height: 8),
          Card(
            child: Column(
              children: [
                SwitchListTile(
                  secondary: const Icon(Icons.dark_mode_outlined),
                  title: const Text('Dark Mode'),
                  subtitle: const Text('Calm dark interface contrast'),
                  value: widget.currentThemeMode == ThemeMode.dark ||
                      (widget.currentThemeMode == ThemeMode.system && isDark),
                  onChanged: (val) {
                    widget.onThemeModeChanged?.call(val ? ThemeMode.dark : ThemeMode.light);
                  },
                ),
                const Divider(height: 1),
                ListTile(
                  leading: const Icon(Icons.translate_outlined),
                  title: const Text('Analysis Language'),
                  subtitle: Text(_selectedLanguage),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: _showLanguageDialog,
                ),
              ],
            ),
          ),

          const SizedBox(height: 20),

          // About & Transparency Section
          Text(
            'Transparency & Disclosures',
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight,
            ),
          ),
          const SizedBox(height: 8),
          Card(
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.psychology_outlined),
                  title: const Text('AI Limitations & Ethics'),
                  subtitle: const Text('How TruthLens reaches conclusions'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: _showAiLimitationsDialog,
                ),
                const Divider(height: 1),
                ListTile(
                  leading: const Icon(Icons.dns_outlined),
                  title: const Text('Backend API Server'),
                  subtitle: Text(ApiConfig.baseUrl),
                ),
                const Divider(height: 1),
                ListTile(
                  leading: const Icon(Icons.info_outline),
                  title: const Text('About TruthLens'),
                  subtitle: const Text('Architecture & Project Information'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: _showAboutDialog,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
