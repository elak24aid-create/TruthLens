from pydantic import BaseModel, Field, constr
from typing import Optional
from datetime import datetime
import uuid

class ReportCreate(BaseModel):
    category: str = Field(..., description="Report reason category")
    verdict: str = Field(..., description="The verdict given by the system")
    content_summary: constr(max_length=500) = Field(..., description="Truncated text or description")
    comment: Optional[constr(max_length=1000)] = Field(None, description="Optional user comment")
    source_url: Optional[str] = Field(None, description="Optional URL of the source")
    input_type: str = Field("text", description="Type of input (text, url, image, video)")

class ReportResponse(BaseModel):
    id: str = Field(..., description="Unique report ID")
    category: str = Field(..., description="Report reason category")
    verdict: str = Field(..., description="The verdict given by the system")
    content_summary: str = Field(..., description="Truncated text or description")
    comment: Optional[str] = Field(None, description="Optional user comment")
    source_url: Optional[str] = Field(None, description="Optional URL of the source")
    input_type: str = Field(..., description="Type of input (text, url, image, video)")
    status: str = Field("Submitted", description="Report status")
    submitted_at: str = Field(..., description="ISO datetime of submission")
