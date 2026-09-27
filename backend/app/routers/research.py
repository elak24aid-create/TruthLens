from fastapi import APIRouter, HTTPException
import logging
from urllib.parse import urlparse

from app.schemas.research import ResearchRequest, ResearchResponse, ResearchSource

router = APIRouter(
    prefix="/research",
    tags=["research"],
)

logger = logging.getLogger(__name__)

from functools import lru_cache

@lru_cache(maxsize=100)
def _fetch_ddg_sources(query: str):
    from ddgs import DDGS
    sources = []
    
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            for res in results:
                title = res.get('title', '')
                snippet = res.get('body', '')
                url = res.get('href', '')
                
                source_name = "Unknown"
                if url:
                    from urllib.parse import urlparse
                    domain = urlparse(url).netloc
                    if domain.startswith('www.'):
                        domain = domain[4:]
                    source_name = domain

                sources.append({
                    "title": title,
                    "url": url,
                    "source_name": source_name,
                    "snippet": snippet,
                    "relevance": None,
                    "published_date": None,
                    "direction": _classify_direction(snippet + " " + title)
                })
    except Exception as e:
        logger.error(f"DDG Search error: {e}")
        raise

    return sources


def _classify_direction(snippet: str) -> str:
    snippet_lower = snippet.lower()
    contradicting = sum(1 for w in ['hoax', 'fake', 'debunk', 'false', 'misinformation', 'conspiracy', 'incorrect'] if w in snippet_lower)
    supporting = sum(1 for w in ['confirm', 'true', 'real', 'factual', 'valid', 'accurate'] if w in snippet_lower)
    
    if contradicting > supporting:
        return "contradicting"
    elif supporting > contradicting:
        return "supporting"
    return "neutral"


@router.post("", response_model=ResearchResponse)
async def research_claim(request: ResearchRequest):
    claim = request.claim.strip()
    
    if not claim:
        raise HTTPException(status_code=400, detail="Claim cannot be empty")
        
    if len(claim) < 10:
        return ResearchResponse(
            claim=claim,
            sources=[],
            summary="Claim is too short to perform reliable online research.",
            research_status="insufficient_evidence"
        )
        
    import string
    # Remove punctuation for better search results
    query = claim.translate(str.maketrans('', '', string.punctuation))
    
    sources = []
    try:
        cached_sources = _fetch_ddg_sources(query)
        sources = [ResearchSource(**s) for s in cached_sources]
    except Exception as e:
        logger.error(f"Search API error: {e}")
        return ResearchResponse(
            claim=claim,
            sources=[],
            summary="An error occurred while connecting to the research service.",
            research_status="error"
        )
        
    if not sources:
        return ResearchResponse(
            claim=claim,
            sources=[],
            summary="Insufficient online evidence found.",
            research_status="success"
        )
        
    # Generate a simple summary based on sources
    domains = [s.source_name for s in sources if s.source_name]
    domain_str = ", ".join(domains[:3])
    if len(domains) > 3:
        domain_str += f" and {len(domains) - 3} others"
        
    summary = f"Research found {len(sources)} relevant sources discussing this topic, including coverage from {domain_str}. " \
              f"The retrieved evidence provides additional context but online search results do not by themselves establish absolute truth."
              
    return ResearchResponse(
        claim=claim,
        sources=sources,
        summary=summary,
        research_status="success"
    )
