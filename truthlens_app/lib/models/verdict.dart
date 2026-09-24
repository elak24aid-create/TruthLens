import 'package:flutter/material.dart';
import '../core/constants/app_colors.dart';

enum VerdictType {
  likelyGenuine,
  likelyMisleading,
  unverified,
  satire,
  insufficientEvidence;

  static VerdictType fromString(String val) {
    switch (val.toLowerCase().trim()) {
      case 'likely genuine':
      case 'genuine':
        return VerdictType.likelyGenuine;
      case 'likely misleading':
      case 'misleading':
      case 'fake':
        return VerdictType.likelyMisleading;
      case 'satire':
        return VerdictType.satire;
      case 'insufficient evidence':
        return VerdictType.insufficientEvidence;
      default:
        return VerdictType.unverified;
    }
  }

  String get displayName {
    switch (this) {
      case VerdictType.likelyGenuine:
        return 'Likely Genuine';
      case VerdictType.likelyMisleading:
        return 'Likely Misleading';
      case VerdictType.unverified:
        return 'Unverified';
      case VerdictType.satire:
        return 'Satire';
      case VerdictType.insufficientEvidence:
        return 'Insufficient Evidence';
    }
  }

  Color get color {
    switch (this) {
      case VerdictType.likelyGenuine:
        return AppColors.verdictGenuine;
      case VerdictType.likelyMisleading:
        return AppColors.verdictMisleading;
      case VerdictType.unverified:
        return AppColors.verdictUnverified;
      case VerdictType.satire:
        return AppColors.verdictSatire;
      case VerdictType.insufficientEvidence:
        return AppColors.verdictInsufficient;
    }
  }

  Color get backgroundColor {
    switch (this) {
      case VerdictType.likelyGenuine:
        return AppColors.verdictGenuineBg;
      case VerdictType.likelyMisleading:
        return AppColors.verdictMisleadingBg;
      case VerdictType.unverified:
        return AppColors.verdictUnverifiedBg;
      case VerdictType.satire:
        return AppColors.verdictSatireBg;
      case VerdictType.insufficientEvidence:
        return AppColors.verdictInsufficientBg;
    }
  }

  IconData get icon {
    switch (this) {
      case VerdictType.likelyGenuine:
        return Icons.verified_outlined;
      case VerdictType.likelyMisleading:
        return Icons.warning_amber_rounded;
      case VerdictType.unverified:
        return Icons.help_outline_rounded;
      case VerdictType.satire:
        return Icons.sentiment_very_satisfied_outlined;
      case VerdictType.insufficientEvidence:
        return Icons.info_outline_rounded;
    }
  }
}
