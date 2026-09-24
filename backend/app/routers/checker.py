from fastapi import APIRouter, HTTPException, status
from backend.app.schemas.checker import CheckTextRequest, CheckUrlRequest, CheckUrlResponse, AnalysisResult
from backend.app.services.preprocessor import preprocess_news_text
from backend.app.services.language_detector import detect_language
from backend.app.services.source_credibility import analyze_source_credibility
from backend.app.services.evidence_aggregator import aggregate_evidence
from backend.app.services.url_extractor import fetch_and_extract_article
from backend.app.ml.predictor import get_predictor
from backend.app.services.online_research import perform_online_research

router = APIRouter(tags=["News Checker"])


@router.post("/check-text", response_model=AnalysisResult)
def check_text(request: CheckTextRequest):
    """
    Analyzes news headline, body text, or social media forward.
    Executes preprocessing, language detection, source extraction,
    ML probability prediction, and multi-signal evidence aggregation.
    """
    try:
        raw_text = request.text

        # 1. Preprocess & extract stylistic patterns
        preprocessed = preprocess_news_text(raw_text)
        if not preprocessed["cleaned_text"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Submitted text contains no readable characters.",
            )

        # 2. Language Detection
        lang_info = detect_language(preprocessed["cleaned_text"])

        # 3. Source Credibility Check
        source_info = analyze_source_credibility(preprocessed["cleaned_text"])

        # 4. ML Model Prediction
        predictor = get_predictor()
        ml_result = predictor.predict(preprocessed["cleaned_text"])
        
        # 4.5. Online Research
        fact_checks = perform_online_research(preprocessed["cleaned_text"][:200]) # only use first 200 chars for search query

        # 5. Multi-Signal Evidence Aggregation
        result = aggregate_evidence(
            text=preprocessed["cleaned_text"],
            preprocessed=preprocessed,
            lang_info=lang_info,
            source_info=source_info,
            ml_result=ml_result,
            fact_checks=fact_checks,
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while analyzing the news content: {str(e)}",
        )

@router.post("/check-url", response_model=CheckUrlResponse)
def check_url(request: CheckUrlRequest):
    """
    Validates URL (SSRF protection), safely fetches the HTML, and extracts the article metadata and text.
    The client will then use this extracted text to call /check-text.
    """
    try:
        extracted = fetch_and_extract_article(request.url)
        return CheckUrlResponse(
            url=request.url,
            title=extracted["title"],
            description=extracted["description"],
            source_name=extracted["source_name"],
            published_at=extracted["published_at"],
            article_text=extracted["article_text"],
            claim_text=extracted["claim_text"],
            status="success"
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze the URL due to an unexpected error.",
        )

from fastapi import UploadFile, File
from backend.app.schemas.checker import CheckImageResponse, CheckVideoResponse
from backend.app.services.ocr_service import extract_text_from_image

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB

@router.post("/check-image", response_model=CheckImageResponse)
async def check_image(file: UploadFile = File(...)):
    """
    Validates uploaded image and extracts text via OCR.
    """
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Please upload JPEG, PNG, or WEBP."
        )

    image_bytes = await file.read()
    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is too large. Maximum size is 10MB."
        )
    if not image_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file uploaded."
        )

    try:
        ocr_text = await extract_text_from_image(image_bytes)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    if not ocr_text or len(ocr_text.strip()) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No readable news text was detected in this image."
        )
    
    # Clean the text minimally for the ML model
    claim_text = " ".join(ocr_text.split())

    return CheckImageResponse(
        status="success",
        ocr_text=ocr_text,
        claim_text=claim_text
    )
from backend.app.services.video_service import extract_text_from_video

ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime", "video/x-matroska"}
MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50 MB

@router.post("/check-video", response_model=CheckVideoResponse)
async def check_video(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported video format. Please upload MP4, WEBM, or MOV."
        )

    video_bytes = await file.read()
    if len(video_bytes) > MAX_VIDEO_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is too large. Maximum size is 50MB."
        )
    if not video_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file uploaded."
        )

    try:
        vid_data = await extract_text_from_video(video_bytes)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process video: {str(e)}"
        )

    ocr_text = vid_data.get("text", "")
    if not ocr_text or len(ocr_text.strip()) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No readable news text was found in the sampled video frames."
        )

    # Clean text for ML
    claim_text = " ".join([line for line in ocr_text.splitlines() if not line.startswith("[")])
    claim_text = " ".join(claim_text.split())

    return CheckVideoResponse(
        status="success",
        ocr_text=ocr_text,
        claim_text=claim_text,
        duration_sec=vid_data.get("duration_sec"),
        frames_sampled=vid_data.get("frames_sampled", 0),
        timestamps=vid_data.get("timestamps", [])
    )
