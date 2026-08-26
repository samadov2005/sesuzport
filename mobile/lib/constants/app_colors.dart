import 'package:flutter/material.dart';

class AppColors {
  // Brand Primary (Emerald / Teal)
  static const Color primary = Color(0xFF0D9488);        // Teal 600
  static const Color primaryLight = Color(0xFF14B8A6);   // Teal 500
  static const Color primaryDark = Color(0xFF0F766E);    // Teal 700
  static const Color accent = Color(0xFF10B981);         // Emerald 500

  // Dark Theme Palette
  static const Color darkBackground = Color(0xFF0F172A);  // Slate 900
  static const Color darkSurface = Color(0xFF1E293B);     // Slate 800
  static const Color darkSurfaceLight = Color(0xFF334155);// Slate 700
  static const Color darkTextPrimary = Color(0xFFF8FAFC); // Slate 50
  static const Color darkTextSecondary = Color(0xFF94A3B8);// Slate 400
  static const Color darkTextMuted = Color(0xFF64748B);   // Slate 500

  // Light Theme Palette
  static const Color lightBackground = Color(0xFFF1F5F9); // Slate 100
  static const Color lightSurface = Color(0xFFFFFFFF);    // Pure White
  static const Color lightSurfaceLight = Color(0xFFE2E8F0);// Slate 200
  static const Color lightTextPrimary = Color(0xFF0F172A); // Slate 900
  static const Color lightTextSecondary = Color(0xFF475569);// Slate 600
  static const Color lightTextMuted = Color(0xFF94A3B8);  // Slate 400

  // Fallback defaults
  static const Color background = Color(0xFF0F172A);
  static const Color surface = Color(0xFF1E293B);
  static const Color surfaceLight = Color(0xFF334155);
  static const Color textPrimary = Color(0xFFF8FAFC);
  static const Color textSecondary = Color(0xFF94A3B8);
  static const Color textMuted = Color(0xFF64748B);

  // Status & Traffic Lights
  static const Color safeGreen = Color(0xFF22C55E);     // Green 500
  static const Color warnYellow = Color(0xFFF59E0B);    // Amber 500
  static const Color dangerRed = Color(0xFFEF4444);     // Red 500
  static const Color infoBlue = Color(0xFF3B82F6);      // Blue 500
  static const Color purple = Color(0xFF8B5CF6);        // Purple 500

  // Gradients
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [Color(0xFF0D9488), Color(0xFF10B981)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient goldGradient = LinearGradient(
    colors: [Color(0xFFF59E0B), Color(0xFFD97706)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
}

class AppThemeColors {
  final bool isDark;
  const AppThemeColors(this.isDark);

  Color get background => isDark ? AppColors.darkBackground : AppColors.lightBackground;
  Color get surface => isDark ? AppColors.darkSurface : AppColors.lightSurface;
  Color get surfaceLight => isDark ? AppColors.darkSurfaceLight : AppColors.lightSurfaceLight;
  Color get textPrimary => isDark ? AppColors.darkTextPrimary : AppColors.lightTextPrimary;
  Color get textSecondary => isDark ? AppColors.darkTextSecondary : AppColors.lightTextSecondary;
  Color get textMuted => isDark ? AppColors.darkTextMuted : AppColors.lightTextMuted;

  List<BoxShadow> get cardShadow => isDark
      ? []
      : [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ];
}

extension BuildContextTheme on BuildContext {
  bool get isDark => Theme.of(this).brightness == Brightness.dark;
  AppThemeColors get colors => AppThemeColors(isDark);
}
