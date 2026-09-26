from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class VerdictEnum(str, Enum):
    LIKELY_GENUINE = "Likely Genuine"
    LIKELY_MISLEADING = "Likely Misleading"
    LIKELY_FALSE = "Likely False"
    UNVERIFIED = "Unverified"
    SATIRE = "Satire"
    INSUFFICIENT_EVIDENCE = "Insufficient Evidence"


class VerificationMode(str, Enum):
    GOOGLE_GROUNDED = "GOOGLE GROUNDED"
    GOOGLE_FACT_CHECK = "GOOGLE FACT CHECK"
    WEB_RESEARCH = "WEB RESEARCH"
    HYBRID = "HYBRID"
    LOCAL_ML_BASELINE = "LOCAL ML BASELINE"
    OFFLINE = "OFFLINE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT EVIDENCE"


class SignalStatusEnum(str, Enum):
    FOUND = "found"
    NOT_FOUND = "not_found"
    CONFLICTING = "conflicting"


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "TruthLens API"
    version: str = "1.0.0"
    environment: str = "development"
    ml_model_loaded: bool = False
    research_available: bool = False
    news_available: bool = False


class SignalItem(BaseModel):
    category: str = Field(..., description="E.g., 'ML Assessment', 'Source Information'")
    status: SignalStatusEnum = Field(..., description="'found', 'not_found', or 'conflicting'")
    label: str = Field(..., description="Short summary tag")
    score: Optional[int] = Field(None, description="Optional numerical score out of 100")
    explanation: str = Field(..., description="Human-understandable explanation")


class EvidenceItem(BaseModel):
    # Unified model
    source_type: Optional[str] = Field("web_search", description="'fact_check', 'google_grounding', 'web_search'")
    publisher: str = Field(..., description="Name of the reporting entity or publisher")
    title: str = Field(..., description="Title of the relevant report or article")
    url: Optional[str] = Field(None, description="Direct URL to external verification or source")
    domain: Optional[str] = Field(None, description="Domain name for source independence grouping")
    relationship: str = Field(..., description="'supporting', 'conflicting', 'context', 'unrelated'")
    claim_supported: Optional[str] = Field(None, description="If this evidence supports a claim, which one?")
    claim_contradicted: Optional[str] = Field(None, description="If this evidence contradicts a claim, which one?")
    published_date: Optional[str] = Field(None, description="Publication or check date")
    retrieved_at: Optional[str] = Field(None, description="When TruthLens pulled this evidence")
    citation_type: Optional[str] = Field("Search Result", description="e.g., 'Grounding Citation', 'Fact Check DB'")
    source_independence: Optional[bool] = Field(True, description="Whether this is judged as an independent verification")
    evidence_excerpt: Optional[str] = Field(None, description="Relevant extracted snippet")
    
    # Legacy fallbacks for Flutter UI / internal code compat
    @property
    def source(self) -> str:
        return self.publisher
        
    @property
    def date(self) -> str:
        return self.published_date
        
    @property
    def explanation(self) -> str:
        return self.evidence_excerpt or self.title
