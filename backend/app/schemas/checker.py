from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator
from .common import VerdictEnum, SignalItem, EvidenceItem, VerificationMode


class CheckTextRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=50000, description="News headline, article body, or social media message to analyze")

    @field_validator("text")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        clean = v.strip()
        if len(clean) < 10:
            raise ValueError("News text must be at least 10 characters of readable content.")
        return clean


class CheckUrlRequest(BaseModel):
    url: str = Field(..., min_length=5, max_length=2000, description="URL of the news article to inspect")

    @field_validator("url")
    @classmethod
    def validate_url_format(cls, v: str) -> str:
        clean = v.strip()
        if not (clean.startswith("http://") or clean.startswith("https://")):
            raise ValueError("URL must start with http:// or https://")
        return clean

class CheckUrlResponse(BaseModel):
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    source_name: Optional[str] = None
    published_at: Optional[str] = None
    article_text: str
    claim_text: str
    status: str

class CheckImageResponse(BaseModel):
    status: str
    ocr_text: str
    claim_text: str

class CheckVideoResponse(BaseModel):
    status: str
    ocr_text: str
    claim_text: str
    duration_sec: Optional[float] = None
    frames_sampled: int
    timestamps: List[str]

class ExtractedMetadata(BaseModel):
    claims_found: List[str] = Field(default_factory=list)
    media_authenticity_notes: List[str] = Field(default_factory=list)

class AnalysisResult(BaseModel):
    verdict: VerdictEnum = Field(..., description="Evidence-based classification verdict")
    confidence: Optional[int] = Field(None, ge=0, le=100, description="Confidence percentage assessment")
    verification_mode: VerificationMode = Field(..., description="The method used to verify this claim")
    language: str = Field(default="English", description="Detected language of the content")
    summary: str = Field(..., description="Executive summary of the credibility analysis")
    why_this_verdict: List[str] = Field(default_factory=list, description="Bullet points explaining how the assessment was derived")
    signals: List[SignalItem] = Field(default_factory=list, description="Categorized multi-signal assessment breakdown")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Supporting, conflicting, or contextual evidence citations")
    extracted_metadata: ExtractedMetadata = Field(default_factory=ExtractedMetadata, description="Metadata if extracted via URL or rich text")
    search_time_ms: int = Field(default=0, description="Time taken to perform online search")
    limitations: List[str] = Field(default_factory=list, description="Any limitations encountered during search")
    analyzed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
