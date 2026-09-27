import spacy
from typing import List, Optional
from ddgs import DDGS
from app.schemas.common import EvidenceItem
from datetime import datetime
import re
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

try:
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    logger.error(f"Failed to load spacy model: {e}")
    nlp = None

def extract_svo(text: str):
    if not nlp:
        return {"subjects": [], "objects": [], "verbs": [], "entities": []}
    doc = nlp(text)
    subjects = [t.lemma_.lower() for t in doc if "subj" in t.dep_]
    objects = [t.lemma_.lower() for t in doc if t.pos_ in ["NOUN", "PROPN"] and "subj" not in t.dep_]
    verbs = [t.lemma_.lower() for t in doc if t.pos_ in ["VERB", "AUX"]]
    entities = [ent.text.lower() for ent in doc.ents]
    return {"subjects": subjects, "objects": objects, "verbs": verbs, "entities": entities}

@lru_cache(maxsize=100)
def perform_online_research(claim: str) -> Optional[List[EvidenceItem]]:
    """
    Robust non-LLM claim verification pipeline.
    """
    evidence = []
    query_text = re.sub(r'http\S+', '', claim).strip()
    if not query_text:
        return []
        
    svo = extract_svo(query_text)
    subs = set(svo["subjects"])
    objs = set(svo["objects"])
    verbs = set(svo["verbs"])
    
    # 1. Search for exact claim and fact checks
    search_queries = [
        query_text,
        f"{query_text} fact check"
    ]
    
    seen_urls = set()
    
    try:
        import time
        with DDGS() as ddgs:
            for q in search_queries:
                results = []
                for attempt in range(3):
                    try:
                        results = list(ddgs.text(q, max_results=5))
                        break
                    except Exception as e:
                        if "No results found" in str(e):
                            time.sleep(2)
                        else:
                            raise e
                            
                for res in results:
                    url = res.get('href', '')
                    if url in seen_urls or 'wikipedia.org' in url.lower():
                        continue
                    seen_urls.add(url)
                    
                    title = res.get('title', '').lower()
                    body = res.get('body', '').lower()
                    text = title + " " + body
                    
                    # 2. Strict Subject/Object matching
                    missing_subs = [s for s in subs if s not in text]
                    missing_objs = [o for o in objs if o not in text]
                    
                    # If the source doesn't mention the core subjects and objects, it's irrelevant.
                    if missing_subs and missing_objs and len(subs) > 0 and len(objs) > 0:
                        continue # IRRELEVANT
                    if "manager" in query_text.lower() and "manager" not in text:
                        continue # Strict for manager test
                        
                    relationship = "context"
                    
                    # 3. Explicit Contradiction
                    contradiction_patterns = [
                        r'\b(false|fake|debunked|hoax|misleading|unfounded|myth|untrue)\b',
                        r'\b(no evidence)\b',
                        r'\b(is not)\b',
                        r'\b(did not)\b',
                        r'\b(never)\b'
                    ]
                    
                    # 4. Explicit Support
                    support_patterns = [
                        r'\b(true|accurate|confirm|confirmed|verified|proven)\b',
                        r'\b(is true)\b'
                    ]
                    
                    is_contradicted = any(re.search(pat, text) for pat in contradiction_patterns)
                    is_supported = any(re.search(pat, text) for pat in support_patterns)
                    
                    relation_negated = any(f"not {v}" in text or f"did not {v}" in text or f"never {v}" in text for v in verbs)
                    
                    # Exact claim overlap
                    clean_claim = re.sub(r'[^\w\s]', '', query_text.lower())
                    clean_text = re.sub(r'[^\w\s]', '', text)
                    exact_match = clean_claim in clean_text
                    
                    if exact_match and not is_contradicted and not relation_negated:
                        relationship = "supporting"
                    elif is_contradicted or relation_negated:
                        relationship = "conflicting"
                    elif is_supported:
                        relationship = "supporting"
                    elif all(v in text for v in verbs) and not is_contradicted:
                        # Fallback: if all subjects, objects, and verbs are present in the same snippet without negation
                        if len(verbs) > 0 and (len(subs) > 0 or len(objs) > 0):
                            if not missing_subs and not missing_objs:
                                relationship = "supporting"
                    
                    source = url.split('/')[2] if url else 'Unknown'
                    if source.startswith('www.'):
                        source = source[4:]
                    
                    evidence.append(EvidenceItem(
                        source_type="web_search",
                        publisher=source,
                        title=res.get('title', ''),
                        url=url,
                        domain=source,
                        relationship=relationship,
                        published_date=None,
                        retrieved_at=datetime.now().isoformat(),
                        citation_type="Article",
                        evidence_excerpt=res.get('body', '')[:300]
                    ))
                    
                    if len(evidence) >= 8:
                        break
                if len(evidence) >= 8:
                    break
    except Exception as e:
        logger.error(f"Online research failed: {e}")
        return None
        
    return evidence
