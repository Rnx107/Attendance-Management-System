import 'package:flutter/material.dart';

/// ---------------------------------------------
/// MAIN BRAND COLORS
/// ---------------------------------------------

class AppColors {
  // Primary (Kathmandu University main identity colors)
  static const Color primaryBlue = Color(0xFF0051BA); // KU Blue (Strong)
  static const Color primaryCrimson = Color(0xFFE8000D); // KU Crimson (Accent)

  // Secondary / Support Colors
  static const Color secondaryNight = Color(0xFF003459);
  static const Color secondaryLake = Color(0xFF2767FF);
  static const Color secondarySky = Color(0xFF73CBF2);
  static const Color neutralFog = Color(0xFF8E9FBC);
  static const Color neutralSteam = Color(0xFFdde5ed);

  // Warm / Highlight Colors
  static const Color warmBrick = Color(0xFF971B2F);
  static const Color warmWheat = Color(0xFFF2A900);
  static const Color warmTerraCotta = Color(0xFFC66E4E);

  // Accent Colors / Feedback
  static const Color accentYellow = Color(0xFFFFC82D);
  static const Color errorRed = Color(0xFFFF3042);
  static const Color successGreen = Color(0xFF4CAF50);

  // Greys
  static const Color greyShade1 = Color(0xFF85898A);
  static const Color greyLight = Color(0xFFF5F5F5);
  static const Color greyDark = Color(0xFF424242);
}

/// ---------------------------------------------
/// TEXT STYLES (Optional Constants)
/// ---------------------------------------------

class TextStyles {
  static const TextStyle heading1 = TextStyle(
    fontSize: 24,
    fontWeight: FontWeight.bold,
    color: AppColors.primaryBlue,
  );

  static const TextStyle heading2 = TextStyle(
    fontSize: 20,
    fontWeight: FontWeight.w600,
    color: AppColors.primaryCrimson,
  );

  static const TextStyle bodyText = TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.normal,
    color: AppColors.greyDark,
  );
}

/// ---------------------------------------------
/// EXAMPLE USAGE
/// ---------------------------------------------
///
/// In your app Theme:
///
/// ThemeData(
///   primaryColor: AppColors.primaryBlue,
///   accentColor: AppColors.primaryCrimson,
///   scaffoldBackgroundColor: AppColors.greyLight,
///   textTheme: TextTheme(
///     headline1: TextStyles.heading1,
///     headline2: TextStyles.heading2,
///     bodyText1: TextStyles.bodyText,
///   ),
/// );
