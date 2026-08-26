import 'package:flutter/material.dart';

class AppColors {
  // Brand Primary & Accents (Emerald / Teal)
  static const Color primary = Color(0xFF0F766E);       // Teal 700
  static const Color primaryLight = Color(0xFF14B8A6);  // Teal 500
  static const Color primaryDark = Color(0xFF115E59);   // Teal 800
  static const Color accent = Color(0xFF06B6D4);        // Cyan 500

  // Background & Surfaces
  static const Color background = Color(0xFF0F172A);    // Slate 900
  static const Color surface = Color(0xFF1E293B);       // Slate 800
  static const Color surfaceLight = Color(0xFF334155);  // Slate 700
  static const Color cardBg = Color(0xFF1E293B);

  // Status Colors
  static const Color safeGreen = Color(0xFF10B981);     // Emerald 500
  static const Color warnYellow = Color(0xFFF59E0B);    // Amber 500
  static const Color dangerRed = Color(0xFFEF4444);     // Red 500
  static const Color infoBlue = Color(0xFF3B82F6);      // Blue 500
  static const Color purple = Color(0xFF8B5CF6);        // Purple 500

  // Text Colors
  static const Color textPrimary = Color(0xFFF8FAFC);   // Slate 50
  static const Color textSecondary = Color(0xFF94A3B8); // Slate 400
  static const Color textMuted = Color(0xFF64748B);     // Slate 500
  static const Color textDark = Color(0xFF0F172A);

  // Gradients
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [Color(0xFF0F766E), Color(0xFF14B8A6)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient cardGradient = LinearGradient(
    colors: [Color(0xFF1E293B), Color(0xFF0F172A)],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );

  static const LinearGradient goldGradient = LinearGradient(
    colors: [Color(0xFFF59E0B), Color(0xFFD97706)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
}
