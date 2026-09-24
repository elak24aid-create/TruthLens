from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime, timezone
import uuid

from backend.app.schemas.report import ReportCreate, ReportResponse

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
)

# In-memory storage for simplicity (acting as our CommunityRepository)
# Note: For production with Firebase, this would be swapped out with a Firestore client.
_reports_db = []

@router.post("", response_model=ReportResponse)
def submit_report(report: ReportCreate):
    new_report = ReportResponse(
        id=str(uuid.uuid4()),
        category=report.category,
        verdict=report.verdict,
        content_summary=report.content_summary,
        comment=report.comment,
        source_url=report.source_url,
        input_type=report.input_type,
        status="Submitted",
        submitted_at=datetime.now(timezone.utc).isoformat() + "Z"
    )
    _reports_db.append(new_report)
    return new_report

@router.get("", response_model=List[ReportResponse])
def get_reports():
    # Only return necessary fields to preserve privacy.
    # In a real app with PII, we would strip user IDs here.
    return sorted(_reports_db, key=lambda r: r.submitted_at, reverse=True)
