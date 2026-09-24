from pydantic import BaseModel, Field
from typing import List, Optional

class ResearchRequest(BaseModel):
    claim: str = Field(..., description="The news claim to research")

class ResearchSource(BaseModel):
    title: str = Field(..., description="Title of the retrieved source")
    url: str = Field(..., description="URL of the source")
    source_name: str = Field(..., description="Name of the publisher or domain")
    snippet: str = Field(..., description="Relevant snippet from the source")
    relevance: Optional[float] = Field(None, description="Relevance score (if available)")
    published_date: Optional[str] = Field(None, description="Publication date (if available)")
    direction: str = Field("neutral", description="supporting, contradicting, or neutral")

class ResearchResponse(BaseModel):
    claim: str = Field(..., description="The original claim")
    sources: List[ResearchSource] = Field(..., description="List of retrieved sources")
    summary: str = Field(..., description="Generated summary based on evidence")
    research_status: str = Field(..., description="Status of research (e.g. 'success', 'error', 'insufficient_evidence')")
