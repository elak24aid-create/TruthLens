import 'package:flutter/material.dart';
import '../home/home_screen.dart';
import '../checker/checker_screen.dart';
import '../history/history_screen.dart';
import '../saved/saved_screen.dart';
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
  final List<bool> _visitedTabs = [true, false, false, false, false];

  void _navigateToTab(int index, {String? initialText}) {
    setState(() {
      _currentIndex = index;
      _visitedTabs[index] = true;
      if (initialText != null) {
        _checkerInitialText = initialText;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final screens = [
      _visitedTabs[0] ? HomeScreen(
        onCheckNewsPressed: () => _navigateToTab(1),
        onCheckText: (text) => _navigateToTab(1, initialText: text),
      ) : const SizedBox.shrink(),
      _visitedTabs[1] ? CheckerScreen(initialText: _checkerInitialText) : const SizedBox.shrink(),
      _visitedTabs[2] ? const HistoryScreen() : const SizedBox.shrink(),
      _visitedTabs[3] ? const SavedScreen() : const SizedBox.shrink(),
      _visitedTabs[4] ? ProfileScreen(
        currentThemeMode: widget.currentThemeMode,
        onThemeModeChanged: widget.onThemeModeChanged,
      ) : const SizedBox.shrink(),
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
            ? AppColors.primary.withValues(alpha: 0.4)
            : AppColors.primaryLight.withValues(alpha: 0.15),
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
            icon: Icon(Icons.bookmark_border),
            selectedIcon: Icon(Icons.bookmark, color: AppColors.primaryLight),
            label: 'Saved',
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
