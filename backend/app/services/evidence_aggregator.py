from typing import Dict, Any, List
from backend.app.schemas.common import VerdictEnum, SignalItem, SignalStatusEnum, EvidenceItem
from backend.app.schemas.checker import AnalysisResult


def aggregate_evidence(
    text: str,
    preprocessed: Dict[str, Any],
    lang_info: Dict[str, Any],
    source_info: Dict[str, Any],
    ml_result: Dict[str, Any],
    fact_checks: List[EvidenceItem] = None,
) -> AnalysisResult:
    """
    Multi-signal aggregation engine.
    Combines ML inference, source credibility, language stylistic patterns,
    and factual evidence into an explainable verdict.
    Never outputs 100% True or 100% Fake.
    """
    fact_checks = fact_checks or []
    signals: List[SignalItem] = []
    why_this_verdict: List[str] = []

    word_count = preprocessed.get("word_count", 0)
    sensational_score = preprocessed.get("sensational_score", 0)
    flags = preprocessed.get("flags", [])

    # 1. Evaluate Source Signal
    is_satire = source_info.get("is_satire", False)
    if is_satire:
        signals.append(
            SignalItem(
                category="Source Information",
                status=SignalStatusEnum.FOUND,
                label="Identified Satirical Publisher",
                score=100,
                explanation=f"Content originates from known humor/satirical outlet ({source_info.get('publisher')}).",
            )
        )
        why_this_verdict.append("The source is officially registered as satirical/humorous commentary.")
        return AnalysisResult(
            verdict=VerdictEnum.SATIRE,
            confidence=95,
            language=lang_info["language"],
            summary="This article is published by a recognized satire publication and is intended for humor rather than factual news.",
            why_this_verdict=why_this_verdict,
            signals=signals,
            evidence=[],
        )

    if source_info.get("status") == "found":
        signals.append(
            SignalItem(
                category="Source Information",
                status=SignalStatusEnum.FOUND,
                label=f"Publisher: {source_info.get('publisher')}",
                explanation=source_info.get("explanation", "Source domain recognized."),
            )
        )
    else:
        signals.append(
            SignalItem(
                category="Source Information",
                status=SignalStatusEnum.NOT_FOUND,
                label="Unattributed Source",
                explanation="No verifiable publisher URL or domain was provided in the query.",
            )
        )

    # 2. Evaluate ML Signal
    if ml_result.get("is_loaded") and ml_result.get("prediction"):
        pred = ml_result["prediction"]
        conf = ml_result["confidence"]
        influential = ml_result.get("influential_terms", [])

        explanation = (
            f"Trained TF-IDF model classified text as {pred} with {conf}% confidence."
        )
        if influential:
            explanation += f" Top contributing terms: {', '.join(influential[:4])}."

        signals.append(
            SignalItem(
                category="ML Assessment",
                status=SignalStatusEnum.FOUND,
                label=f"Statistical Model: {pred}",
                score=conf,
                explanation=explanation,
            )
        )
    else:
        signals.append(
            SignalItem(
                category="ML Assessment",
                status=SignalStatusEnum.NOT_FOUND,
                label="Model Awaiting Dataset",
                explanation=(
                    "ML classification weights are awaiting training on benchmark dataset. "
                    "Evaluation relies on stylistic, structural, and transparency signals."
                ),
            )
        )

    # 3. Evaluate Content & Stylistic Signals
    if flags:
        signals.append(
            SignalItem(
                category="Content Signals",
                status=SignalStatusEnum.FOUND,
                label="Stylistic Red Flags Detected",
                score=sensational_score,
                explanation="; ".join(flags),
            )
        )
    else:
        signals.append(
            SignalItem(
                category="Content Signals",
                status=SignalStatusEnum.NOT_FOUND,
                label="Standard Editorial Tone",
                score=10,
                explanation="Text does not exhibit excessive shouting, clickbait phrases, or abnormal punctuation.",
            )
        )

    # 4. Evaluate Fact Check Evidence
    if fact_checks:
        signals.append(
            SignalItem(
                category="Fact-Check Search",
                status=SignalStatusEnum.FOUND,
                label=f"{len(fact_checks)} Related Fact-Checks Found",
                explanation=f"Found {len(fact_checks)} independent review(s) related to this claim.",
            )
        )
    else:
        signals.append(
            SignalItem(
                category="Fact-Check Search",
                status=SignalStatusEnum.NOT_FOUND,
                label="No Direct Fact-Check Found",
                explanation="No public fact-check record matched this exact claim. (Note: Not found does NOT imply the claim is true or false).",
            )
        )

    # 5. Synthesis & Final Verdict Computation
    # Check for short or vacuous text
    if word_count < 5:
        verdict = VerdictEnum.INSUFFICIENT_EVIDENCE
        confidence = 50
        summary = "The provided text is too brief to extract verifiable factual claims or establish credibility."
        why_this_verdict.append("Submitted text contains fewer than 5 words.")
        why_this_verdict.append("Insufficient context for reliable statistical or fact-checking analysis.")
        return AnalysisResult(
            verdict=verdict,
            confidence=confidence,
            language=lang_info["language"],
            summary=summary,
            why_this_verdict=why_this_verdict,
            signals=signals,
            evidence=fact_checks,
        )

    if len(fact_checks) == 0:
        verdict = VerdictEnum.INSUFFICIENT_EVIDENCE
        confidence = 50
        summary = "No verifiable online evidence could be found to support or refute this claim."
        why_this_verdict.append("Online research returned no results.")
        return AnalysisResult(
            verdict=verdict,
            confidence=confidence,
            language=lang_info["language"],
            summary=summary,
            why_this_verdict=why_this_verdict,
            signals=signals,
            evidence=fact_checks,
        )

    # Determine verdict based on signals
    misleading_points = 0.0
    genuine_points = 0.0
    base_confidence = 50

    if ml_result.get("is_loaded") and ml_result.get("prediction"):
        base_confidence = ml_result["confidence"]
        if ml_result["prediction"] == "Likely Misleading":
            misleading_points += 50
        else:
            genuine_points += 50

    if sensational_score > 40:
        misleading_points += 20
        why_this_verdict.append(f"Content displays strong sensationalist patterns (score: {sensational_score}/100).")
    elif sensational_score <= 15:
        genuine_points += 10
        why_this_verdict.append("Neutral, non-sensational phrasing observed.")

    if source_info.get("tier") == "High Transparency":
        genuine_points += 30
        why_this_verdict.append(f"Source publisher '{source_info.get('publisher')}' has documented editorial oversight.")
    elif source_info.get("status") == "not_found":
        why_this_verdict.append("Source could not be verified from known transparent news organizations.")

    # Incorporate DDG fact_checks evidence
    supporting_count = sum(1 for e in fact_checks if e.relationship == "supporting")
    conflicting_count = sum(1 for e in fact_checks if e.relationship == "conflicting")

    if conflicting_count > 0 and conflicting_count >= supporting_count:
        misleading_points += 100  # Strong override
        why_this_verdict.append(f"Found {conflicting_count} online fact-check(s) refuting or contradicting this claim.")
        base_confidence = max(base_confidence, 85 + min(10, conflicting_count * 2))
    elif supporting_count > 0 and supporting_count > conflicting_count:
        genuine_points += 100  # Strong override
        why_this_verdict.append(f"Found {supporting_count} online fact-check(s) supporting or confirming this claim.")
        base_confidence = max(base_confidence, 85 + min(10, supporting_count * 2))

    # Calculate final verdict using ML confidence as the base
    if misleading_points >= genuine_points + 10:
        verdict = VerdictEnum.LIKELY_MISLEADING
        # Cap confidence at 99 so it doesn't say 100%
        confidence = min(99, max(55, base_confidence))
        summary = (
            "Available signals indicate patterns commonly associated with misleading or unverified viral claims."
        )
        if "Language patterns" not in why_this_verdict and conflicting_count == 0:
            why_this_verdict.append("Language patterns and content signals align with misleading narratives.")
    elif genuine_points >= misleading_points + 10:
        verdict = VerdictEnum.LIKELY_GENUINE
        # Cap confidence at 99
        confidence = min(99, max(55, base_confidence))
        summary = (
            "Available signals reflect standard journalistic conventions and transparent reporting structures."
        )
        if "Signals align" not in why_this_verdict and supporting_count == 0:
            why_this_verdict.append("Signals align with standard, non-sensational factual reporting.")
    else:
        verdict = VerdictEnum.UNVERIFIED
        confidence = 55
        summary = (
            "Conflicting or inconclusive signals were observed. The claim cannot be verified without further primary documentation."
        )
        why_this_verdict.append("Signals are balanced or ambiguous between credible and unverified markers.")

    return AnalysisResult(
        verdict=verdict,
        confidence=confidence,
        language=lang_info["language"],
        summary=summary,
        why_this_verdict=why_this_verdict,
        signals=signals,
        evidence=fact_checks,
    )
