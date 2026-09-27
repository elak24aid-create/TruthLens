import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

# google-genai sdk
from google import genai
from google.genai import types
from google.genai.errors import APIError

from app.schemas.common import EvidenceItem, VerdictEnum

logger = logging.getLogger(__name__)

# Daily Usage limits to ensure cost safety
GOOGLE_DAILY_GROUNDING_LIMIT = int(os.environ.get("GOOGLE_DAILY_GROUNDING_LIMIT", 50))
USAGE_FILE = "google_usage.json"

def check_and_increment_usage() -> bool:
    """Checks daily limit, returns True if OK, False if blocked"""
    try:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        usage_data = {}
        if os.path.exists(USAGE_FILE):
            with open(USAGE_FILE, "r") as f:
                usage_data = json.load(f)
        
        current_date = usage_data.get("date")
        count = usage_data.get("count", 0)

        if current_date != today:
            usage_data = {"date": today, "count": 1}
        else:
            if count >= GOOGLE_DAILY_GROUNDING_LIMIT:
                logger.warning(f"Google Grounding unavailable — free-safe limit reached ({count}/{GOOGLE_DAILY_GROUNDING_LIMIT})")
                return False
            usage_data["count"] = count + 1
            
        with open(USAGE_FILE, "w") as f:
            json.dump(usage_data, f)
            
        return True
    except Exception as e:
        logger.error(f"Failed to track Google API usage: {e}")
        # Default to True so a filesystem error doesn't break everything, but log heavily
        return True


# Pydantic schemas for Gemini Structured Output
class ExtractedClaim(BaseModel):
    claim_text: str = Field(description="The factual claim extracted")
    is_verifiable: bool = Field(description="Can this claim be fact-checked?")

class EvidenceAssessment(BaseModel):
    url: str = Field(description="The exact URL of the source")
    title: str = Field(description="The title of the source page")
    publisher: str = Field(description="The publisher or domain name")
    relationship: str = Field(description="supporting, conflicting, context, or unrelated")
    explanation: str = Field(description="How this source relates to the claim")

class GeminiVerificationResult(BaseModel):
    claims: List[ExtractedClaim] = Field(default_factory=list, description="List of factual claims found in the text/media")
    summary: str = Field(description="A brief paragraph summarizing the truthfulness based ONLY on retrieved evidence")
    evidence_assessment: List[EvidenceAssessment] = Field(default_factory=list, description="Assessment of retrieved grounding sources")
    verdict: str = Field(description="One of: LIKELY TRUE, LIKELY MISLEADING, LIKELY FALSE, INSUFFICIENT EVIDENCE, UNVERIFIED")
    confidence: Optional[int] = Field(None, description="0-100 confidence score based on evidence strength")
    uncertainty: List[str] = Field(default_factory=list, description="Any uncertainties or missing context")
    media_authenticity_notes: List[str] = Field(default_factory=list, description="For images/videos: notes on visual claims, NOT deepfake detection")


class GoogleVerificationService:
    def __init__(self):
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        self.model_id = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
        self.client = None
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)

    def is_available(self) -> bool:
        return self.client is not None

    def verify_claim(self, content_text: str, content_type: str = "text", media_parts: List[Any] = None) -> Dict[str, Any]:
        """
        Uses Gemini with Google Search Grounding to verify a claim.
        Returns a dict containing the parsed GeminiVerificationResult, grounding metadata, and raw evidence items.
        """
        if not self.is_available():
            return {"status": "error", "reason": "GOOGLE GROUNDING UNAVAILABLE"}

        if not check_and_increment_usage():
            return {"status": "error", "reason": "FREE LIMIT REACHED"}

        try:
            # Prepare contents
            contents = []
            if media_parts:
                contents.extend(media_parts)
            
            prompt = f"""
Analyze the following {content_type} for factual accuracy.
Content: "{content_text}"

Instructions:
1. Extract the main verifiable claims.
2. Use Google Search to find high-quality, independent evidence.
3. Determine if the claims are supported, contradicted, or unverified.
4. Separate the factual claim verification from media authenticity (if this is an image/video, describe what it shows but do NOT claim it is a deepfake unless you have explicit search evidence of it).
5. Never invent or hallucinate URLs. Only use sources retrieved via Search.
6. If no strong evidence is found, the verdict MUST be INSUFFICIENT EVIDENCE.
            """
            contents.append(prompt)

            # Use Google Search tool
            search_tool = {"google_search": {}}

            response = self.client.models.generate_content(
                model=self.model_id,
                contents=contents,
                config=types.GenerateContentConfig(
                    tools=[search_tool],
                    response_mime_type="application/json",
                    response_schema=GeminiVerificationResult,
                    temperature=0.2,
                )
            )

            # Parse structured output
            try:
                result_obj = json.loads(response.text)
            except Exception:
                result_obj = {}

            # Parse Grounding Metadata
            grounding_metadata = None
            evidence_items = []
            has_grounding = False

            # Check if grounding metadata exists in the response chunks
            for candidate in response.candidates:
                if candidate.grounding_metadata:
                    grounding_metadata = candidate.grounding_metadata
                    has_grounding = True
                    # Extract sources
                    if hasattr(grounding_metadata, 'grounding_chunks'):
                        for chunk in grounding_metadata.grounding_chunks:
                            if hasattr(chunk, 'web') and chunk.web:
                                # Map to EvidenceItem
                                url = getattr(chunk.web, 'uri', '')
                                title = getattr(chunk.web, 'title', '')
                                if url:
                                    domain = url.split('/')[2] if '://' in url else ''
                                    
                                    # Try to find matching assessment from the structured output
                                    relationship = "context"
                                    explanation = title
                                    for assessment in result_obj.get("evidence_assessment", []):
                                        if assessment.get("url") == url or assessment.get("title") == title:
                                            relationship = assessment.get("relationship", "context")
                                            explanation = assessment.get("explanation", title)
                                            break

                                    evidence_items.append(
                                        EvidenceItem(
                                            source_type="google_grounding",
                                            publisher=domain,
                                            title=title,
                                            url=url,
                                            domain=domain,
                                            relationship=relationship,
                                            retrieved_at=datetime.now(timezone.utc).isoformat(),
                                            citation_type="Grounding Citation",
                                            evidence_excerpt=explanation
                                        )
                                    )

            return {
                "status": "success",
                "has_grounding": has_grounding,
                "parsed_result": result_obj,
                "evidence_items": evidence_items
            }

        except APIError as e:
            logger.error(f"Gemini API Error: {e}")
            return {"status": "error", "reason": f"API Error: {e.code}"}
        except Exception as e:
            logger.error(f"Google Service Error: {e}")
            return {"status": "error", "reason": str(e)}

