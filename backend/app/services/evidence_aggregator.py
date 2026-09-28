from typing import Dict, Any, List
from app.schemas.common import VerdictEnum, SignalItem, SignalStatusEnum, EvidenceItem, VerificationMode
from app.schemas.checker import AnalysisResult, ExtractedMetadata

def aggregate_evidence(
    text: str,
    preprocessed: Dict[str, Any],
    lang_info: Dict[str, Any],
    source_info: Dict[str, Any],
    ml_result: Dict[str, Any],
    evidence_items: List[EvidenceItem] = None,
    verification_mode: VerificationMode = VerificationMode.WEB_RESEARCH,
    extracted_metadata: ExtractedMetadata = None,
    search_time_ms: int = 0,
    google_verdict: str = None,
    google_summary: str = None
) -> AnalysisResult:
    """
    Multi-signal aggregation engine.
    Combines Fact Checks, Google Grounding, Web Research, ML inference, and credibility.
    """
    signals: List[SignalItem] = []
    why_this_verdict: List[str] = []
    
    if evidence_items is None:
        evidence_items = []
        
    word_count = preprocessed.get("word_count", 0)
    flags = preprocessed.get("flags", [])
    
    # ML Signal
    if ml_result.get("is_loaded") and ml_result.get("prediction"):
        signals.append(
            SignalItem(
                category="ML Assessment",
                status=SignalStatusEnum.FOUND,
                label=f"Statistical Model: {ml_result['prediction']}",
                score=ml_result["confidence"],
                explanation=f"TF-IDF classification confidence: {ml_result['confidence']}%."
            )
        )
    
    # Evidence Signal
    if evidence_items:
        signals.append(
            SignalItem(
                category="External Evidence",
                status=SignalStatusEnum.FOUND,
                label=f"{len(evidence_items)} Sources Found",
                explanation=f"Found {len(evidence_items)} external citations via {verification_mode.value}."
            )
        )
    else:
        signals.append(
            SignalItem(
                category="External Evidence",
                status=SignalStatusEnum.NOT_FOUND,
                label="No Online Evidence",
                explanation="No verifiable public evidence could be retrieved."
            )
        )

    # Tally evidence
    supporting_count = sum(1 for e in evidence_items if e.relationship == "supporting")
    conflicting_count = sum(1 for e in evidence_items if e.relationship == "conflicting")
    wiki_conflict = any(e.publisher == "wikipedia" and e.relationship == "conflicting" for e in evidence_items)

    # Base signals logic for insufficient text (only if NO evidence at all was found)
    if word_count < 5 and not wiki_conflict and conflicting_count == 0 and supporting_count == 0 and not (extracted_metadata and extracted_metadata.claims_found) and content_not_media(extracted_metadata):
        return AnalysisResult(
            verdict=VerdictEnum.INSUFFICIENT_EVIDENCE,
            confidence=0,
            verification_mode=verification_mode,
            language=lang_info.get("language", "English"),
            summary="The provided text is too brief to extract verifiable factual claims or establish credibility.",
            why_this_verdict=["Submitted text contains fewer than 5 words.", "Insufficient context for verification."],
            signals=signals,
            evidence=evidence_items,
            extracted_metadata=extracted_metadata or ExtractedMetadata(),
            search_time_ms=search_time_ms
        )

    # Priority: Google/Gemini Structured output overrides if it used grounding successfully
    if verification_mode == VerificationMode.GOOGLE_GROUNDED and google_verdict:
        # Convert Gemini Verdict
        verdict = VerdictEnum.UNVERIFIED
        if "MISLEADING" in google_verdict:
            verdict = VerdictEnum.LIKELY_MISLEADING
        elif "FALSE" in google_verdict:
            verdict = VerdictEnum.LIKELY_FALSE
        elif "TRUE" in google_verdict or "GENUINE" in google_verdict:
            verdict = VerdictEnum.LIKELY_GENUINE
        elif "INSUFFICIENT" in google_verdict:
            verdict = VerdictEnum.INSUFFICIENT_EVIDENCE
            
        why_this_verdict.append("Google Search Grounding was utilized for this verdict.")
        if supporting_count > 0:
            why_this_verdict.append(f"Found {supporting_count} supporting grounded sources.")
        if conflicting_count > 0:
            why_this_verdict.append(f"Found {conflicting_count} conflicting grounded sources.")
            
        return AnalysisResult(
            verdict=verdict,
            confidence=None, # Confidence is optional, don't fabricate
            verification_mode=verification_mode,
            language=lang_info.get("language", "English"),
            summary=google_summary or "Verified using Google Search Grounding.",
            why_this_verdict=why_this_verdict,
            signals=signals,
            evidence=evidence_items,
            extracted_metadata=extracted_metadata or ExtractedMetadata(),
            search_time_ms=search_time_ms
        )

    # Fallback Logic (Fact Check / Web Research / ML)
    if supporting_count == 0 and conflicting_count == 0:
        if verification_mode == VerificationMode.OFFLINE:
            summary = "Device is offline. Showing cached or local ML baseline."
            verdict = VerdictEnum.UNVERIFIED
            conf = ml_result.get("confidence") if ml_result.get("is_loaded") else 0
        else:
            verdict = VerdictEnum.INSUFFICIENT_EVIDENCE
            conf = 0
            summary = "No strong supporting or conflicting evidence could be found online."
            why_this_verdict.append("The system found general context but no explicit verification.")
            why_this_verdict.append("The TF-IDF ML model's prediction is discarded due to lack of verifiable external evidence.")
            if ml_result.get("is_loaded"):
                verification_mode = VerificationMode.LOCAL_ML_BASELINE
    
    elif wiki_conflict:
        verdict = VerdictEnum.LIKELY_MISLEADING
        conf = 99
        summary = "Online evidence contradicts or refutes the core claims."
        why_this_verdict.append("Authoritative encyclopedic source explicitly refutes the identity claim.")
        
    elif conflicting_count > 0 and conflicting_count >= supporting_count:
        verdict = VerdictEnum.LIKELY_MISLEADING
        conf = 85 + min(10, conflicting_count * 2)
        summary = "Online evidence contradicts or refutes the core claims."
        why_this_verdict.append(f"Found {conflicting_count} online fact-check(s) refuting this claim.")
        if supporting_count > 0 and supporting_count == conflicting_count:
            if wiki_conflict:
                # Strong identity conflict overrides a tie
                pass
            else:
                verdict = VerdictEnum.INSUFFICIENT_EVIDENCE
                summary = "Online evidence is conflicting and inconclusive."
                why_this_verdict.append("Found equal amounts of supporting and refuting claims.")
                conf = 0

    elif supporting_count > 0 and supporting_count > conflicting_count:
        verdict = VerdictEnum.LIKELY_GENUINE
        conf = 85 + min(10, supporting_count * 2)
        summary = "Online evidence supports and verifies the core claims."
        why_this_verdict.append(f"Found {supporting_count} online fact-check(s) supporting this claim.")

    else:
        verdict = VerdictEnum.UNVERIFIED
        conf = 55
        summary = "Conflicting or inconclusive signals were observed."
        why_this_verdict.append("Signals are balanced or ambiguous.")

    return AnalysisResult(
        verdict=verdict,
        confidence=conf,
        verification_mode=verification_mode,
        language=lang_info.get("language", "English"),
        summary=summary,
        why_this_verdict=why_this_verdict,
        signals=signals,
        evidence=evidence_items,
        extracted_metadata=extracted_metadata or ExtractedMetadata(),
        search_time_ms=search_time_ms
    )

def content_not_media(extracted_metadata: ExtractedMetadata) -> bool:
    if not extracted_metadata:
        return True
    return len(extracted_metadata.media_authenticity_notes) == 0
