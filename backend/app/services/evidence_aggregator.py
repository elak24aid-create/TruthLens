import logging
from typing import List, Dict, Any, Optional
from app.schemas.common import (
    VerdictEnum, SignalStatusEnum, VerificationMode,
    SignalItem
)
from app.schemas.checker import AnalysisResult, ExtractedMetadata
from app.schemas.common import EvidenceItem

logger = logging.getLogger(__name__)

def get_source_weight(domain: str) -> float:
    if not domain:
        return 1.0
    domain = domain.lower()
    if domain.endswith(".edu") or domain.endswith(".gov") or domain in ["wikipedia.org", "nasa.gov", "science.nasa.gov", "britannica.com"]:
        return 3.0
    if domain in ["reuters.com", "apnews.com", "bbc.com", "bbc.co.uk", "snopes.com", "politifact.com", "factcheck.org"]:
        return 2.5
    if domain in ["facebook.com", "reddit.com", "quora.com", "twitter.com", "x.com", "tiktok.com", "instagram.com"]:
        return 0.2
    return 1.0

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
    signals: List[SignalItem] = []
    why_this_verdict: List[str] = []
    
    if evidence_items is None:
        evidence_items = []
        
    word_count = preprocessed.get("word_count", 0)
    
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

    support_score = 0.0
    conflict_score = 0.0
    supporting_count = 0
    conflicting_count = 0
    
    for e in evidence_items:
        weight = get_source_weight(e.domain)
        if e.relationship == "DIRECT_SUPPORT":
            support_score += weight
            supporting_count += 1
        elif e.relationship == "DIRECT_CONTRADICTION":
            conflict_score += weight
            conflicting_count += 1

    if word_count < 5 and conflict_score == 0 and support_score == 0 and not (extracted_metadata and extracted_metadata.claims_found) and content_not_media(extracted_metadata):
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

    if support_score == 0 and conflict_score == 0:
        verdict = VerdictEnum.INSUFFICIENT_EVIDENCE
        conf = 0
        summary = "No strong supporting or conflicting evidence could be found online."
        why_this_verdict.append("The system found general context but no explicit verification.")
    
    elif conflict_score > 0 and conflict_score >= support_score:
        verdict = VerdictEnum.LIKELY_MISLEADING
        conf = int(min(100, 75 + (conflict_score * 5)))
        summary = "Online evidence contradicts or refutes the core claims."
        why_this_verdict.append(f"Found {conflicting_count} online source(s) refuting this claim (Weighted Score: {conflict_score:.1f}).")
        if support_score > 0 and support_score == conflict_score:
            verdict = VerdictEnum.INSUFFICIENT_EVIDENCE
            summary = "Online evidence is conflicting and inconclusive."
            why_this_verdict.append("Found equal weights of supporting and refuting claims.")
            conf = 0

    elif support_score > 0 and support_score > conflict_score:
        verdict = VerdictEnum.LIKELY_GENUINE
        conf = int(min(100, 75 + (support_score * 5)))
        summary = "Online evidence supports and verifies the core claims."
        why_this_verdict.append(f"Found {supporting_count} online source(s) supporting this claim (Weighted Score: {support_score:.1f}).")
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
