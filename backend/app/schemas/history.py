from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from .common import VerdictEnum


class HistoryItemCreate(BaseModel):
    text_snippet: str = Field(..., max_length=1000)
    verdict: VerdictEnum
    confidence: int
    summary: str
    input_type: str = Field(default="text", description="text, url, image, video, news")
    url: Optional[str] = None
    analysis_result: Optional[dict] = None
    research_result: Optional[dict] = None


class HistoryItemResponse(BaseModel):
    id: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    text_snippet: str
    verdict: VerdictEnum
    confidence: int
    summary: str
    input_type: str
    url: Optional[str] = None
    analysis_result: Optional[dict] = None
    research_result: Optional[dict] = None
