import re
from typing import Dict, Any


def detect_language(text: str) -> Dict[str, Any]:
    """
    Detects language using character script ranges and common stopword heuristics.
    Supports English, Hindi, Tamil, Telugu, Malayalam, Kannada, Bengali, Arabic, Spanish, French.
    """
    if not text or not text.strip():
        return {"language": "English", "iso_code": "en", "confidence": 1.0}

    # Count characters in distinct script ranges
    counts = {
        "Tamil": len(re.findall(r"[\u0B80-\u0BFF]", text)),
        "Hindi": len(re.findall(r"[\u0900-\u097F]", text)),  # Devanagari
        "Telugu": len(re.findall(r"[\u0C00-\u0C7F]", text)),
        "Malayalam": len(re.findall(r"[\u0D00-\u0D7F]", text)),
        "Kannada": len(re.findall(r"[\u0C80-\u0CFF]", text)),
        "Bengali": len(re.findall(r"[\u0980-\u09FF]", text)),
        "Arabic": len(re.findall(r"[\u0600-\u06FF]", text)),
    }

    # Find maximum script match
    total_special = sum(counts.values())
    if total_special > 5:
        best_lang = max(counts, key=counts.get)
        iso_map = {
            "Tamil": "ta",
            "Hindi": "hi",
            "Telugu": "te",
            "Malayalam": "ml",
            "Kannada": "kn",
            "Bengali": "bn",
            "Arabic": "ar",
        }
        return {
            "language": best_lang,
            "iso_code": iso_map.get(best_lang, "und"),
            "confidence": round(counts[best_lang] / total_special, 2),
        }

    # Latin-script heuristic check for Spanish / French vs English
    text_lower = text.lower()
    spanish_markers = ["el ", "la ", "de ", "en ", "los ", "las ", "por ", "con ", "noticias", "según"]
    french_markers = ["le ", "la ", "les ", "des ", "pour ", "dans ", "avec ", "selon", "actualités"]

    es_score = sum(1 for m in spanish_markers if m in text_lower)
    fr_score = sum(1 for m in french_markers if m in text_lower)

    if es_score >= 4 and es_score > fr_score:
        return {"language": "Spanish", "iso_code": "es", "confidence": 0.85}
    elif fr_score >= 4:
        return {"language": "French", "iso_code": "fr", "confidence": 0.85}

    # Default to English
    return {"language": "English", "iso_code": "en", "confidence": 0.95}
