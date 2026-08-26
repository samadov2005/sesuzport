import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'constants/app_colors.dart';
import 'constants/theme_notifier.dart';
import 'constants/app_strings.dart';
import 'screens/splash_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await ThemeNotifier.instance.init();
  await AppLocaleNotifier.instance.init();

  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
    ),
  );

  runApp(const SesportApp());
}

class SesportApp extends StatelessWidget {
  const SesportApp({super.key});

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: Listenable.merge([
        ThemeNotifier.instance,
        AppLocaleNotifier.instance,
      ]),
      builder: (context, _) {
        return MaterialApp(
          title: 'SESPORT',
          debugShowCheckedModeBanner: false,
          themeMode: ThemeNotifier.instance.themeMode,

          // ☀️ CLEAN LIGHT THEME
          theme: ThemeData(
            useMaterial3: true,
            brightness: Brightness.light,
            scaffoldBackgroundColor: AppColors.lightBackground,
            primaryColor: AppColors.primary,
            colorScheme: const ColorScheme.light(
              primary: AppColors.primary,
              secondary: AppColors.accent,
              surface: AppColors.lightSurface,
            ),
            fontFamily: 'Roboto',
            appBarTheme: const AppBarTheme(
              backgroundColor: AppColors.lightSurface,
              elevation: 0,
              centerTitle: true,
              titleTextStyle: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: AppColors.lightTextPrimary,
              ),
              iconTheme: IconThemeData(color: AppColors.lightTextPrimary),
            ),
          ),

          // 🌙 MODERN DARK THEME
          darkTheme: ThemeData(
            useMaterial3: true,
            brightness: Brightness.dark,
            scaffoldBackgroundColor: AppColors.darkBackground,
            primaryColor: AppColors.primaryLight,
            colorScheme: const ColorScheme.dark(
              primary: AppColors.primaryLight,
              secondary: AppColors.accent,
              surface: AppColors.darkSurface,
            ),
            fontFamily: 'Roboto',
            appBarTheme: const AppBarTheme(
              backgroundColor: AppColors.darkSurface,
              elevation: 0,
              centerTitle: true,
              titleTextStyle: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: AppColors.darkTextPrimary,
              ),
              iconTheme: IconThemeData(color: AppColors.darkTextPrimary),
            ),
          ),

          home: const SplashScreen(),
        );
      },
    );
  }
}
