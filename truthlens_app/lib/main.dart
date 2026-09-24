import 'package:flutter/material.dart';
import 'config/theme_config.dart';
import 'core/constants/app_strings.dart';
import 'features/auth/splash_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const TruthLensApp());
}

class TruthLensApp extends StatefulWidget {
  const TruthLensApp({super.key});

  @override
  State<TruthLensApp> createState() => _TruthLensAppState();
}

class _TruthLensAppState extends State<TruthLensApp> {
  ThemeMode _themeMode = ThemeMode.system;

  void _handleThemeModeChanged(ThemeMode mode) {
    setState(() {
      _themeMode = mode;
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: AppStrings.appName,
      debugShowCheckedModeBanner: false,
      theme: ThemeConfig.lightTheme,
      darkTheme: ThemeConfig.darkTheme,
      themeMode: _themeMode,
      home: SplashScreen(
        currentThemeMode: _themeMode,
        onThemeModeChanged: _handleThemeModeChanged,
      ),
    );
  }
}
