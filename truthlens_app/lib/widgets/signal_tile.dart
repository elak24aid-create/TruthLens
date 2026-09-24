import 'package:flutter/material.dart';
import '../models/signal_item.dart';
import '../core/constants/app_colors.dart';

class SignalTile extends StatelessWidget {
  final SignalItem signal;

  const SignalTile({super.key, required this.signal});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    IconData statusIcon;
    Color statusColor;
    String statusBadge;

    if (signal.isFound) {
      statusIcon = Icons.check_circle_outline_rounded;
      statusColor = AppColors.verdictGenuine;
      statusBadge = 'EVIDENCE FOUND';
    } else if (signal.isConflicting) {
      statusIcon = Icons.error_outline_rounded;
      statusColor = AppColors.verdictMisleading;
      statusBadge = 'CONFLICTING';
    } else {
      statusIcon = Icons.remove_circle_outline_rounded;
      statusColor = AppColors.verdictInsufficient;
      statusBadge = 'NOT FOUND';
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF1E293B) : const Color(0xFFF8FAFC),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isDark ? const Color(0xFF334155) : const Color(0xFFE2E8F0),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(statusIcon, color: statusColor, size: 18),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  signal.category,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: statusColor.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  statusBadge,
                  style: TextStyle(
                    color: statusColor,
                    fontSize: 10,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 0.3,
                  ),
                ),
              ),
            ],
          ),
          if (signal.label.isNotEmpty) ...[
            const SizedBox(height: 6),
            Text(
              signal.label,
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: isDark ? const Color(0xFFE2E8F0) : const Color(0xFF334155),
              ),
            ),
          ],
          const SizedBox(height: 4),
          Text(
            signal.explanation,
            style: TextStyle(
              fontSize: 12,
              height: 1.4,
              color: isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight,
            ),
          ),
        ],
      ),
    );
  }
}
