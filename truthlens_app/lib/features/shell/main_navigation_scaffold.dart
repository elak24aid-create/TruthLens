import 'package:flutter/material.dart';
import '../home/home_screen.dart';
import '../checker/checker_screen.dart';
import '../history/history_screen.dart';
import '../reports/community_reports_screen.dart';
import '../profile/profile_screen.dart';
import '../../core/constants/app_colors.dart';

class MainNavigationScaffold extends StatefulWidget {
  final ValueChanged<ThemeMode>? onThemeModeChanged;
  final ThemeMode currentThemeMode;

  const MainNavigationScaffold({
    super.key,
    this.onThemeModeChanged,
    this.currentThemeMode = ThemeMode.system,
  });

  @override
  State<MainNavigationScaffold> createState() => _MainNavigationScaffoldState();
}

class _MainNavigationScaffoldState extends State<MainNavigationScaffold> {
  int _currentIndex = 0;
  String? _checkerInitialText;

  void _navigateToTab(int index, {String? initialText}) {
    setState(() {
      _currentIndex = index;
      if (initialText != null) {
        _checkerInitialText = initialText;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final screens = [
      HomeScreen(
        onCheckNewsPressed: () => _navigateToTab(1),
        onCheckText: (text) => _navigateToTab(1, initialText: text),
      ),
      CheckerScreen(initialText: _checkerInitialText),
      const HistoryScreen(),
      const CommunityReportsScreen(),
      ProfileScreen(
        currentThemeMode: widget.currentThemeMode,
        onThemeModeChanged: widget.onThemeModeChanged,
      ),
    ];

    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: screens,
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: _navigateToTab,
        backgroundColor: isDark ? AppColors.surfaceDark : AppColors.surfaceLight,
        indicatorColor: isDark
            ? AppColors.primary.withOpacity(0.4)
            : AppColors.primaryLight.withOpacity(0.15),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home, color: AppColors.primaryLight),
            label: 'Home',
          ),
          NavigationDestination(
            icon: Icon(Icons.fact_check_outlined),
            selectedIcon: Icon(Icons.fact_check, color: AppColors.primaryLight),
            label: 'Check News',
          ),
          NavigationDestination(
            icon: Icon(Icons.history_outlined),
            selectedIcon: Icon(Icons.history, color: AppColors.primaryLight),
            label: 'History',
          ),
          NavigationDestination(
            icon: Icon(Icons.report_outlined),
            selectedIcon: Icon(Icons.report, color: AppColors.primaryLight),
            label: 'Reports',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline),
            selectedIcon: Icon(Icons.person, color: AppColors.primaryLight),
            label: 'Profile',
          ),
        ],
      ),
    );
  }
}
