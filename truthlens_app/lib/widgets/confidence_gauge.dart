import 'package:flutter/material.dart';
import '../core/constants/app_colors.dart';

class ConfidenceGauge extends StatelessWidget {
  final int confidence;
  final Color activeColor;

  const ConfidenceGauge({
    super.key,
    required this.confidence,
    required this.activeColor,
  });

  @override
  Widget build(BuildContext context) {
    final clamped = confidence.clamp(0, 100);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Text(
          '$clamped%',
          style: TextStyle(
            fontSize: 44,
            fontWeight: FontWeight.w800,
            color: isDark ? AppColors.textPrimaryDark : AppColors.textPrimaryLight,
            letterSpacing: -1.0,
          ),
        ),
        const SizedBox(height: 4),
        Tooltip(
          message: 'This score represents the weight of supporting vs conflicting verified evidence, not a direct probability of truth.',
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'Evidence Assessment Score',
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w500,
                  color: isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight,
                ),
              ),
              const SizedBox(width: 4),
              Icon(
                Icons.info_outline,
                size: 14,
                color: isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight,
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),
        ClipRRect(
          borderRadius: BorderRadius.circular(8),
          child: LinearProgressIndicator(
            value: clamped / 100.0,
            minHeight: 8,
            backgroundColor: isDark ? const Color(0xFF334155) : const Color(0xFFE2E8F0),
            valueColor: AlwaysStoppedAnimation<Color>(activeColor),
          ),
        ),
      ],
    );
  }
}
