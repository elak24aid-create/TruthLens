from typing import List, Optional
from ddgs import DDGS
from app.schemas.common import EvidenceItem
from datetime import datetime
import re
from functools import lru_cache

@lru_cache(maxsize=100)
def perform_online_research(claim: str) -> Optional[List[EvidenceItem]]:
    """
    Use duckduckgo-search to query fact-checking sites and general news.
    Returns None if search genuinely fails (exception/timeout).
    """
    evidence = []
    
    # Strip URL structures if present to just search text
    query_text = re.sub(r'http\S+', '', claim).strip()
    if not query_text:
        return []
        
    query = f'{query_text}'
    
    try:
        with DDGS() as ddgs:
            # We fetch up to 8 results and filter
            results = list(ddgs.text(query, max_results=8))
            
            for res in results:
                title = res.get('title', '')
                body = res.get('body', '')
                url = res.get('href', '')
                
                # Skip Wikipedia as main verifier
                if 'wikipedia.org' in url.lower():
                    continue
                    
                lower_body = body.lower()
                lower_title = title.lower()
                
                relationship = 'context'
                
                # Better polarity analysis rather than simple "fact" keyword
                if re.search(r'\b(false|fake|debunked|hoax|misleading|unfounded|fabricated|deception|scam|myth)\b', lower_title):
                    relationship = 'conflicting'
                elif re.search(r'\b(fact\s*check(ed)?:?\s*(false|fake|misleading))\b', lower_title):
                    relationship = 'conflicting'
                elif re.search(r'\b(true|accurate|confirm|confirmed|legitimate)\b', lower_title):
                    relationship = 'supporting'
                elif re.search(r'\b(fact\s*check(ed)?:?\s*(true|accurate|correct))\b', lower_title):
                    relationship = 'supporting'
                else:
                    # Look in body for strong signals, avoiding generic words
                    if re.search(r'\b(fact\s*check(ed)?:?\s*(false|fake|misleading|unfounded|hoax|debunked))\b', lower_body) or re.search(r'\b(debunked by)\b', lower_body):
                        relationship = 'conflicting'
                    elif re.search(r'\b(fact\s*check(ed)?:?\s*(true|accurate|correct|legitimate))\b', lower_body):
                        relationship = 'supporting'
                    else:
                        relationship = 'context'
                
                source = url.split('/')[2] if url else 'Unknown'
                if source.startswith('www.'):
                    source = source[4:]
                
                evidence.append(EvidenceItem(
                    source_type="web_search",
                    publisher=source,
                    title=title,
                    url=url,
                    domain=source,
                    relationship=relationship,
                    published_date=None,
                    retrieved_at=datetime.now().isoformat(),
                    citation_type="Article",
                    evidence_excerpt=body[:300] + ('...' if len(body) > 300 else '')
                ))
                
                if len(evidence) >= 5:
                    break
    except Exception as e:
        # Genuine research failure
        print(f"Online research failed: {e}")
        return None
        
    return evidence
