import 'package:flutter/material.dart';
import '../models/signal_item.dart';
import 'signal_tile.dart';
import '../core/constants/app_colors.dart';

class WhyVerdictCard extends StatefulWidget {
  final List<String> reasons;
  final List<SignalItem> signals;
  final String? researchSummary;

  const WhyVerdictCard({
    super.key,
    required this.reasons,
    required this.signals,
    this.researchSummary,
  });

  @override
  State<WhyVerdictCard> createState() => _WhyVerdictCardState();
}

class _WhyVerdictCardState extends State<WhyVerdictCard> {
  bool _isExpanded = true;

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            InkWell(
              onTap: () {
                setState(() {
                  _isExpanded = !_isExpanded;
                });
              },
              borderRadius: BorderRadius.circular(8),
              child: Padding(
                padding: const EdgeInsets.symmetric(vertical: 4.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(
                      children: [
                        const Icon(
                          Icons.psychology_outlined,
                          color: AppColors.primaryLight,
                          size: 22,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'Why This Verdict?',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: isDark
                                ? AppColors.textPrimaryDark
                                : AppColors.textPrimaryLight,
                          ),
                        ),
                      ],
                    ),
                    Icon(
                      _isExpanded
                          ? Icons.keyboard_arrow_up_rounded
                          : Icons.keyboard_arrow_down_rounded,
                      color: isDark
                          ? AppColors.textSecondaryDark
                          : AppColors.textSecondaryLight,
                    ),
                  ],
                ),
              ),
            ),
            if (_isExpanded) ...[
              const SizedBox(height: 12),
              // ML Analysis
              Text(
                'ML Analysis:',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: isDark ? AppColors.textPrimaryDark : AppColors.textPrimaryLight,
                ),
              ),
              const SizedBox(height: 8),
              if (widget.reasons.isNotEmpty) ...[
                ...widget.reasons.map((reason) => Padding(
                      padding: const EdgeInsets.only(bottom: 6.0),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Padding(
                            padding: EdgeInsets.only(top: 5.0, right: 8.0),
                            child: Icon(
                              Icons.fiber_manual_record,
                              size: 8,
                              color: AppColors.primaryLight,
                            ),
                          ),
                          Expanded(
                            child: Text(
                              reason,
                              style: TextStyle(
                                fontSize: 13,
                                height: 1.4,
                                color: isDark
                                    ? AppColors.textSecondaryDark
                                    : AppColors.textSecondaryLight,
                              ),
                            ),
                          ),
                        ],
                      ),
                    )),
              ],
              
              const SizedBox(height: 12),
              // Online Evidence
              Text(
                'Online Evidence:',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: isDark ? AppColors.textPrimaryDark : AppColors.textPrimaryLight,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                widget.researchSummary ?? 'Research in progress or not available.',
                style: TextStyle(
                  fontSize: 13,
                  height: 1.4,
                  color: isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight,
                ),
              ),
              
              const SizedBox(height: 16),
              const Divider(),
              const SizedBox(height: 12),
              // Signal breakdown list
              Text(
                'Individual Signal Analysis',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: isDark
                      ? AppColors.textPrimaryDark
                      : AppColors.textPrimaryLight,
                ),
              ),
              const SizedBox(height: 10),
              ...widget.signals.map((signal) => SignalTile(signal: signal)),
            ],
          ],
        ),
      ),
    );
  }
}
