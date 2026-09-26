import os
import requests
import logging
from typing import List, Optional
from datetime import datetime, timezone

from backend.app.schemas.common import EvidenceItem

logger = logging.getLogger(__name__)

class GoogleFactCheckService:
    def __init__(self):
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        self.base_url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

    def is_available(self) -> bool:
        return bool(self.api_key)

    def search_claims(self, query: str) -> Optional[List[EvidenceItem]]:
        """
        Queries the Google Fact Check Tools API for the given claim.
        Returns a list of EvidenceItems or None if unavailable/error.
        """
        if not self.is_available():
            return None
            
        try:
            params = {
                "key": self.api_key,
                "query": query,
                "pageSize": 3,
                "languageCode": "en-US"
            }
            
            response = requests.get(self.base_url, params=params, timeout=5)
            
            if response.status_code != 200:
                logger.warning(f"Fact Check API returned {response.status_code}: {response.text}")
                return None
                
            data = response.json()
            claims = data.get("claims", [])
            
            evidence_items = []
            for claim in claims:
                claim_text = claim.get("text", "")
                claimant = claim.get("claimant", "")
                claim_date = claim.get("claimDate", "")
                
                for review in claim.get("claimReview", []):
                    publisher = review.get("publisher", {}).get("name", "Unknown Publisher")
                    url = review.get("url", "")
                    title = review.get("title", f"Fact check by {publisher}")
                    rating = review.get("textualRating", "")
                    review_date = review.get("reviewDate", "")
                    
                    # Heuristic to map rating to relationship
                    lower_rating = rating.lower()
                    if any(x in lower_rating for x in ["false", "pants on fire", "fake", "incorrect"]):
                        relationship = "conflicting"
                    elif any(x in lower_rating for x in ["true", "correct", "accurate"]):
                        relationship = "supporting"
                    else:
                        relationship = "context"
                        
                    domain = url.split('/')[2] if '://' in url else publisher
                    
                    evidence_items.append(
                        EvidenceItem(
                            source_type="fact_check",
                            publisher=publisher,
                            title=title,
                            url=url,
                            domain=domain,
                            relationship=relationship,
                            claim_contradicted=claim_text if relationship == "conflicting" else None,
                            claim_supported=claim_text if relationship == "supporting" else None,
                            published_date=review_date or claim_date,
                            retrieved_at=datetime.now(timezone.utc).isoformat(),
                            citation_type="Fact Check API",
                            evidence_excerpt=f"Rated '{rating}' regarding claim: {claim_text}"
                        )
                    )
            
            return evidence_items
            
        except Exception as e:
            logger.error(f"Error querying Fact Check Tools API: {e}")
            return None
