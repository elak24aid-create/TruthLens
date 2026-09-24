from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class VerdictEnum(str, Enum):
    LIKELY_GENUINE = "Likely Genuine"
    LIKELY_MISLEADING = "Likely Misleading"
    UNVERIFIED = "Unverified"
    SATIRE = "Satire"
    INSUFFICIENT_EVIDENCE = "Insufficient Evidence"


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
    category: str = Field(..., description="E.g., 'ML Assessment', 'Source Information', 'Content Signals', 'Fact-Check Search'")
    status: SignalStatusEnum = Field(..., description="'found', 'not_found', or 'conflicting'")
    label: str = Field(..., description="Short summary tag e.g. 'Consistent linguistic patterns'")
    score: Optional[int] = Field(None, description="Optional numerical score out of 100")
    explanation: str = Field(..., description="Human-understandable explanation why this signal applies")


class EvidenceItem(BaseModel):
    source: str = Field(..., description="Name of the reporting entity or publisher")
    title: str = Field(..., description="Title of the relevant report or article")
    url: Optional[str] = Field(None, description="Direct URL to external verification or source")
    date: Optional[str] = Field(None, description="Publication or check date")
    relationship: str = Field(..., description="'supporting', 'conflicting', or 'context'")
    explanation: str = Field(..., description="Summary of how this evidence relates to the claim")
