import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'config/theme_config.dart';
import 'core/constants/app_strings.dart';
import 'features/auth/splash_screen.dart';
import 'services/storage_service.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const TruthLensApp());
}

class TruthLensApp extends StatefulWidget {
  const TruthLensApp({super.key});

  static _TruthLensAppState? of(BuildContext context) => context.findAncestorStateOfType<_TruthLensAppState>();

  @override
  State<TruthLensApp> createState() => _TruthLensAppState();
}

class _TruthLensAppState extends State<TruthLensApp> {
  ThemeMode _themeMode = ThemeMode.system;
  Locale? _locale;

  @override
  void initState() {
    super.initState();
    _loadLocale();
  }

  Future<void> _loadLocale() async {
    final code = await StorageService.getLocale();
    if (code != null && mounted) {
      setState(() {
        _locale = Locale(code);
      });
    }
  }

  void setLocale(Locale locale) {
    setState(() {
      _locale = locale;
    });
    StorageService.saveLocale(locale.languageCode);
  }

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
      locale: _locale,
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [
        Locale('en'),
        Locale('ta'),
        Locale('hi'),
        Locale('te'),
        Locale('ml'),
        Locale('kn'),
        Locale('ja'),
        Locale('ko'),
        Locale('zh'),
        Locale('es'),
        Locale('fr'),
        Locale('de'),
        Locale('ar'),
      ],
      home: SplashScreen(
        currentThemeMode: _themeMode,
        onThemeModeChanged: _handleThemeModeChanged,
      ),
    );
  }
}
