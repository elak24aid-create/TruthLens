from typing import List
from ddgs import DDGS
from backend.app.schemas.common import EvidenceItem
from datetime import datetime

def perform_online_research(claim: str) -> List[EvidenceItem]:
    """
    Use duckduckgo-search to query fact-checking sites and general news.
    """
    evidence = []
    
    try:
        with DDGS() as ddgs:
            # Search query focusing on fact checks
            query = f'{claim} fact check'
            results = list(ddgs.text(query, max_results=5))
            
            for res in results:
                title = res.get('title', '')
                body = res.get('body', '')
                url = res.get('href', '')
                
                # Simple heuristic for relationship
                lower_body = body.lower()
                lower_title = title.lower()
                
                if 'false' in lower_title or 'fake' in lower_title or 'debunked' in lower_title or 'hoax' in lower_title or 'misleading' in lower_title or 'unfounded' in lower_body:
                    relationship = 'conflicting'
                elif 'true' in lower_title or 'accurate' in lower_title or 'confirm' in lower_title or 'confirm' in lower_body or 'fact' in lower_title:
                    relationship = 'supporting'
                else:
                    # If it's a direct news report from a reputable source, it's supporting
                    if any(x in url.lower() for x in ['nasa.gov', 'bbc.', 'reuters.', 'apnews.', 'npr.org']):
                        relationship = 'supporting'
                    else:
                        relationship = 'context'
                    
                source = url.split('/')[2] if url else 'Unknown'
                if source.startswith('www.'):
                    source = source[4:]
                
                evidence.append(EvidenceItem(
                    source=source,
                    title=title,
                    url=url,
                    date=datetime.now().strftime("%Y-%m-%d"),
                    relationship=relationship,
                    explanation=body
                ))
    except Exception:
        pass
        
    return evidence
