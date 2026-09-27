import re
from typing import Dict, Any, List
from app.utils.sanitizer import sanitize_text

# Misinformation linguistic red flags / sensationalism indicators
SENSATIONAL_PATTERNS = [
    r"\bshocking\b",
    r"\bmiracle cure\b",
    r"\bsecret truth\b",
    r"\bthey don'?t want you to know\b",
    r"\bforward to all\b",
    r"\bshare before (it gets )?deleted\b",
    r"\b100% (cured|guaranteed|proven)\b",
    r"\bviral alert\b",
    r"\bmagic remedy\b",
    r"\burgent warning\b",
    r"\bconspiracy revealed\b",
    r"\bbreaking: shocking\b",
    r"\bgovernment hiding\b",
]


def preprocess_news_text(raw_text: str) -> Dict[str, Any]:
    """
    Cleans and analyzes structural and stylistic aspects of input news text.
    Extracts headline vs body, computes linguistic warning signals.
    """
    cleaned = sanitize_text(raw_text)
    if not cleaned:
        return {
            "cleaned_text": "",
            "headline": "",
            "body": "",
            "word_count": 0,
            "char_count": 0,
            "sensational_score": 0,
            "flags": [],
        }

    lines = [line.strip() for line in cleaned.split("\n") if line.strip()]
    headline = lines[0] if lines else ""
    body = " ".join(lines[1:]) if len(lines) > 1 else headline

    words = re.findall(r"\b[A-Za-z0-9_']+\b", cleaned)
    word_count = len(words)
    char_count = len(cleaned)

    # Stylistic warning checks
    flags: List[str] = []

    # 1. Excessive capitalization check (words of length > 3 that are ALL CAPS)
    caps_words = [w for w in words if len(w) > 3 and w.isupper()]
    caps_ratio = len(caps_words) / max(word_count, 1)
    if caps_ratio > 0.20 and len(caps_words) >= 3:
        flags.append("Excessive uppercase lettering often used in sensationalist claims")

    # 2. Repeated punctuation (!!!, ???, !?!)
    repeated_punct = re.findall(r"[!?]{2,}", cleaned)
    if len(repeated_punct) >= 2:
        flags.append("Repeated exclamation or question marks indicating emotional appeal")

    # 3. Sensational keywords pattern matching
    matched_patterns = []
    cleaned_lower = cleaned.lower()
    for pattern in SENSATIONAL_PATTERNS:
        if re.search(pattern, cleaned_lower):
            matched_patterns.append(pattern.replace(r"\b", "").replace(r"\?", "?"))

    if matched_patterns:
        flags.append(f"Sensationalist buzzwords detected: {', '.join(matched_patterns[:3])}")

    # Calculate sensational score (0 to 100)
    score = min(100, int(len(flags) * 30 + caps_ratio * 50))

    return {
        "cleaned_text": cleaned,
        "headline": headline,
        "body": body,
        "word_count": word_count,
        "char_count": char_count,
        "sensational_score": score,
        "flags": flags,
    }
