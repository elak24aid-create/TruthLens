from fastapi import APIRouter, HTTPException, status, UploadFile, File
import time
from app.schemas.checker import CheckTextRequest, CheckUrlRequest, AnalysisResult, ExtractedMetadata
from app.services.preprocessor import preprocess_news_text
from app.services.language_detector import detect_language
from app.services.source_credibility import analyze_source_credibility
from app.services.evidence_aggregator import aggregate_evidence
from app.services.url_extractor import fetch_and_extract_article
from app.ml.predictor import get_predictor
from app.services.online_research import perform_online_research
from app.services.google_service import GoogleVerificationService
from app.services.google_fact_check_service import GoogleFactCheckService
from app.services.ocr_service import extract_text_from_image
from app.services.video_service import extract_text_from_video
from app.schemas.common import VerificationMode, EvidenceItem, VerdictEnum
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["News Checker"])

# Initialize Google services
google_service = GoogleVerificationService()
fact_check_service = GoogleFactCheckService()

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB

ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime", "video/x-matroska"}
MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50 MB

def perform_verification_pipeline(
    raw_text: str,
    content_type: str = "text",
    extracted_metadata: ExtractedMetadata = None,
    media_parts: list = None
) -> AnalysisResult:
    """
    Core verification pipeline used by all endpoints.
    Implements hybrid architecture: Fact Check -> Gemini Grounding -> Web Search -> ML Fallback
    """
    start_time = time.time()
    
    if extracted_metadata and extracted_metadata.ocr_status in ["OCR_UNAVAILABLE", "NO_TEXT_DETECTED"]:
        return AnalysisResult(
            verdict=VerdictEnum.UNVERIFIED,
            confidence=0,
            verification_mode=VerificationMode.OFFLINE,
            language="Unknown",
            summary=f"Media processing failed: {extracted_metadata.ocr_status}",
            why_this_verdict=[f"The system reported: {extracted_metadata.ocr_status}"],
            signals=[],
            evidence=[],
            extracted_metadata=extracted_metadata,
            search_time_ms=0
        )
    
    # 1. Preprocess & Language
    preprocessed = preprocess_news_text(raw_text)
    lang_info = detect_language(preprocessed["cleaned_text"])
    source_info = analyze_source_credibility(preprocessed["cleaned_text"])

    # Extract query logic: For URLs or long text, use the headline to avoid overly long queries
    query_text = preprocessed["headline"] if preprocessed["headline"] else preprocessed["cleaned_text"]
    if len(query_text) > 120:
        query_text = query_text[:120]

    # 2. Local ML Baseline (always computed but may be overridden)
    predictor = get_predictor()
    ml_result = predictor.predict(preprocessed["cleaned_text"])
    
    evidence_items = []
    verification_mode = VerificationMode.WEB_RESEARCH
    google_verdict = None
    google_summary = None

    # Step A: Google Fact Check Tools API (fastest, most authoritative)
    if fact_check_service.is_available() and query_text:
        try:
            fc_results = fact_check_service.search_claims(query_text)
            if fc_results:
                evidence_items.extend(fc_results)
                verification_mode = VerificationMode.FACT_CHECK_API
        except Exception as e:
            logger.error(f"Fact Check API failed: {e}")

    # Step B: Gemini with Google Search Grounding
    if not evidence_items and google_service.is_available() and (query_text or media_parts):
        try:
            # For media without text, we rely entirely on Gemini's multimodal capabilities
            gemini_result = google_service.verify_claim(
                content_text=query_text,
                content_type=content_type,
                media_parts=media_parts
            )
            
            if gemini_result.get("status") == "success":
                parsed = gemini_result.get("parsed_result", {})
                if parsed and gemini_result.get("has_grounding"):
                    # We only trust it if it actually grounded it
                    evidence_items.extend(gemini_result.get("evidence_items", []))
                    if evidence_items:
                        verification_mode = VerificationMode.GOOGLE_GROUNDED
                        google_verdict = parsed.get("verdict")
                        google_summary = parsed.get("summary")
                        
                        # Apply media authenticity notes if any
                        if extracted_metadata and parsed.get("media_authenticity_notes"):
                            extracted_metadata.media_authenticity_notes = parsed["media_authenticity_notes"]
                            
                elif parsed and not evidence_items:
                    # It ran successfully but found no grounding. It's essentially unverified.
                    # We will still fallback to DDGS just in case, or accept lack of evidence.
                    pass
            elif gemini_result.get("reason") == "FREE LIMIT REACHED":
                logger.info("Google daily limit reached, falling back to DDGS web research.")
        except Exception as e:
            logger.error(f"Google Grounding failed: {e}")

    # Step C: Fallback to existing public web research (DDGS)
    if not evidence_items and query_text:
        try:
            ddgs_results = perform_online_research(query_text)
            if ddgs_results:
                evidence_items.extend(ddgs_results)
                verification_mode = VerificationMode.WEB_RESEARCH
        except Exception as e:
            logger.error(f"Web research failed: {e}")

    # Final Aggregation
    search_time_ms = int((time.time() - start_time) * 1000)
    
    result = aggregate_evidence(
        text=preprocessed["cleaned_text"],
        preprocessed=preprocessed,
        lang_info=lang_info,
        source_info=source_info,
        ml_result=ml_result,
        evidence_items=evidence_items,
        verification_mode=verification_mode,
        extracted_metadata=extracted_metadata,
        search_time_ms=search_time_ms,
        google_verdict=google_verdict,
        google_summary=google_summary
    )
    
    return result

@router.post("/check-text", response_model=AnalysisResult)
def check_text(request: CheckTextRequest):
    try:
        if not request.text or len(request.text.strip()) < 5:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Submitted text contains no readable characters or is too short.",
            )
        
        return perform_verification_pipeline(request.text, "text")

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Text check error")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check-url", response_model=AnalysisResult)
def check_url(request: CheckUrlRequest):
    try:
        extracted = fetch_and_extract_article(request.url)
        metadata = ExtractedMetadata(
            title=extracted["title"],
            source_name=extracted["source_name"],
            url=request.url,
            published_at=extracted["published_at"],
            claims_found=[extracted.get("title", "")] if extracted.get("title") else []
        )
        
        return perform_verification_pipeline(
            raw_text=extracted["claim_text"],
            content_type="news article",
            extracted_metadata=metadata
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.exception("URL check error")
        raise HTTPException(status_code=500, detail="Failed to analyze URL.")

@router.post("/check-image", response_model=AnalysisResult)
async def check_image(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    image_bytes = await file.read()
    if len(image_bytes) > MAX_IMAGE_SIZE or not image_bytes:
        raise HTTPException(status_code=400, detail="Invalid file size.")

    try:
        ocr_text, ocr_status = await extract_text_from_image(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    metadata = ExtractedMetadata(
        ocr_text=ocr_text,
        ocr_status=ocr_status,
        claims_found=[ocr_text] if ocr_text and len(ocr_text.strip()) > 5 else []
    )

    # For multimodal Gemini, pass the raw bytes
    media_parts = [{"mime_type": file.content_type, "data": image_bytes}]
    
    # We still provide the OCR text to the pipeline as fallback/text signal
    claim_text = " ".join(ocr_text.split()) if ocr_text else "Image content without obvious text."

    return perform_verification_pipeline(
        raw_text=claim_text,
        content_type="image",
        extracted_metadata=metadata,
        media_parts=media_parts
    )

@router.post("/check-video", response_model=AnalysisResult)
async def check_video(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported video format.")

    video_bytes = await file.read()
    if len(video_bytes) > MAX_VIDEO_SIZE or not video_bytes:
        raise HTTPException(status_code=400, detail="Invalid file size.")

    try:
        vid_data = await extract_text_from_video(video_bytes)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process video: {str(e)}")

    ocr_text = vid_data.get("text", "")
    metadata = ExtractedMetadata(
        duration_sec=vid_data.get("duration_sec"),
        frames_sampled=vid_data.get("frames_sampled", 0),
        ocr_text=ocr_text,
        claims_found=[ocr_text] if ocr_text and len(ocr_text.strip()) > 5 else []
    )

    claim_text = " ".join([line for line in ocr_text.splitlines() if not line.startswith("[")])
    claim_text = " ".join(claim_text.split()) if claim_text else "Video content without obvious text."

    # Gemini API expects video files to be uploaded via the File API for multimodality, 
    # but we can try passing the video bytes directly for small videos (Gemini 3.5 flash lite might support it or not).
    # Since video might be up to 50MB, passing inline bytes might fail. We'll omit multimodal video for now,
    # or rely solely on OCR text + Fact Check/DDGS. 
    # Note: To send video to Gemini multimodally, you usually need to upload it first using genai.Client().files.upload().
    # For now, we'll only send the OCR text to Gemini.

    return perform_verification_pipeline(
        raw_text=claim_text,
        content_type="video",
        extracted_metadata=metadata,
        media_parts=None # Video bytes too large for inline multimodal, sticking to OCR
    )
