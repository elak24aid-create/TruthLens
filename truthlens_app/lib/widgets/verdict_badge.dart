import 'package:flutter/material.dart';
import '../models/verdict.dart';

class VerdictBadge extends StatelessWidget {
  final VerdictType verdict;
  final bool isLarge;

  const VerdictBadge({
    super.key,
    required this.verdict,
    this.isLarge = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: isLarge ? 16 : 10,
        vertical: isLarge ? 8 : 4,
      ),
      decoration: BoxDecoration(
        color: verdict.backgroundColor,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: verdict.color.withOpacity(0.3), width: 1.2),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            verdict.icon,
            size: isLarge ? 20 : 14,
            color: verdict.color,
          ),
          const SizedBox(width: 6),
          Text(
            verdict.displayName.toUpperCase(),
            style: TextStyle(
              color: verdict.color,
              fontSize: isLarge ? 14 : 11,
              fontWeight: FontWeight.bold,
              letterSpacing: 0.5,
            ),
          ),
        ],
      ),
    );
  }
}
