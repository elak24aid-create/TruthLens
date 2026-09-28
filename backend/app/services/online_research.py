import logging
import re
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from functools import lru_cache
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import urllib.parse
import concurrent.futures
from app.schemas.common import EvidenceItem
import spacy

logger = logging.getLogger(__name__)

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = None

def get_wiki_summary(subject: str) -> Optional[str]:
    try:
        from urllib.request import urlopen
        import json
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(subject)}"
        with urlopen(url, timeout=3) as response:
            data = json.loads(response.read().decode())
            return data.get('extract')
    except Exception:
        return None

def check_identity(text: str) -> Optional[EvidenceItem]:
    if not nlp:
        return None
    doc = nlp(text)
    be_verb = None
    for token in doc:
        if token.lemma_ == "be" and token.dep_ == "ROOT":
            be_verb = token
            break
    if not be_verb:
        return None
        
    subj_tokens = []
    attr_tokens = []
    for child in be_verb.children:
        if "subj" in child.dep_:
            subj_tokens = list(child.subtree)
        elif child.dep_ in ["attr", "acomp"]:
            attr_tokens = list(child.subtree)
            
    if subj_tokens and attr_tokens:
        subj = " ".join([t.text for t in subj_tokens]).strip()
        
        attr_core = None
        for t in attr_tokens:
            if t.dep_ in ["attr", "acomp"] and t.head == be_verb:
                attr_core = t.lemma_.lower()
                break
                
        if not attr_core:
            attr_core = attr_tokens[-1].lemma_.lower()
            
        attr_lemmas = [t.lemma_.lower() for t in attr_tokens if not t.is_stop and t.is_alpha]
        if not attr_lemmas:
            return None
        
        # We try both the exact subject and a clean version
        candidates = [subj, " ".join([t.text for t in subj_tokens if t.pos_ in ["NOUN", "PROPN"]]).strip()]
        for candidate in set(candidates):
            summary = get_wiki_summary(candidate)
            if summary:
                # Better matching logic for Wiki
                summary_lower = summary.lower()
                # If ANY of the attributes are explicitly matched in the summary, it's strong direct support
                # Example: "The Sun is a star" -> attr_lemmas = ['star']. "star" in summary -> SUPPORT
                rel = "UNRELATED"
                for lemma in attr_lemmas:
                    if lemma in summary_lower:
                        rel = "DIRECT_SUPPORT"
                        break
                
                if rel == "UNRELATED" and attr_core in summary_lower:
                    rel = "DIRECT_SUPPORT"
                
                if rel == "UNRELATED":
                    # If it's a completely different entity type, maybe it's conflicting
                    # but we keep it contextual for now
                    rel = "CONTEXTUAL"
                
                return EvidenceItem(
                    source_type="web_search",
                    publisher="wikipedia.org",
                    title=f"Wikipedia: {candidate.title()}",
                    url=f"https://en.wikipedia.org/wiki/{candidate.replace(' ', '_')}",
                    domain="wikipedia.org",
                    relationship=rel,
                    published_date=None,
                    retrieved_at=datetime.utcnow().isoformat() + "Z",
                    citation_type="Article",
                    evidence_excerpt=summary[:400] + "..."
                )
    return None

def extract_svo(text: str):
    if not nlp:
        return {"subjects": [], "objects": [], "verbs": [], "entities": []}
    doc = nlp(text)
    subjects = [t.lemma_.lower() for t in doc if "subj" in t.dep_]
    objects = [t.lemma_.lower() for t in doc if t.pos_ in ["NOUN", "PROPN"] and "subj" not in t.dep_]
    verbs = [t.lemma_.lower() for t in doc if t.pos_ in ["VERB", "AUX"]]
    entities = [ent.text.lower() for ent in doc.ents]
    return {"subjects": subjects, "objects": objects, "verbs": verbs, "entities": entities}

def search_ddgs(query: str, max_results: int = 5) -> List[Dict]:
    results = []
    try:
        with DDGS() as ddgs:
            # use a short timeout wrapper if possible, duckduckgo_search has internal retries
            for res in ddgs.text(query, max_results=max_results):
                results.append(res)
    except Exception as e:
        logger.warning(f"DDGS Error for {query}: {e}")
    return results

@lru_cache(maxsize=100)
def perform_online_research(claim: str) -> Optional[List[EvidenceItem]]:
    """
    Robust non-LLM claim verification pipeline.
    """
    evidence = []
    query_text = re.sub(r'http\S+', '', claim).strip()
    if not query_text:
        return []
        
    # Generalized mathematical-expression check
    math_match = re.search(r'^([0-9\s\+\-\*\/\(\)\.]+)\s*=\s*([0-9\.\-]+)$', query_text)
    if math_match:
        left_expr = math_match.group(1).strip()
        right_val = math_match.group(2).strip()
        try:
            allowed_chars = set("0123456789+-*/(). ")
            if all(c in allowed_chars for c in left_expr):
                calculated = eval(left_expr, {"__builtins__": None}, {})
                is_correct = (abs(float(calculated) - float(right_val)) < 1e-5)
                
                rel = "DIRECT_SUPPORT" if is_correct else "DIRECT_CONTRADICTION"
                desc = f"Mathematical evaluation of '{left_expr}' equals {calculated}, which means the statement '{query_text}' is {is_correct}."
                
                evidence.append(EvidenceItem(
                    source_type="computational",
                    publisher="math_evaluator",
                    title="Mathematical Evaluation",
                    url="local://math",
                    domain="local",
                    relationship=rel,
                    published_date=datetime.utcnow().isoformat() + "Z",
                    retrieved_at=datetime.utcnow().isoformat() + "Z",
                    citation_type="Calculation",
                    evidence_excerpt=desc
                ))
                return evidence
        except Exception:
            pass
        
    svo = extract_svo(query_text)
    subs = set(svo["subjects"])
    objs = set(svo["objects"])
    verbs = set(svo["verbs"])
    
    # 1. Parallelize Wiki and DDGS searches
    search_queries = [
        query_text,
        f"{query_text} fact check"
    ]
    
    ddgs_results = []
    wiki_ev = None
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        wiki_future = executor.submit(check_identity, query_text)
        ddgs_futures = [executor.submit(search_ddgs, q, 4) for q in search_queries]
        
        try:
            wiki_ev = wiki_future.result(timeout=4)
        except Exception:
            pass
            
        for future in concurrent.futures.as_completed(ddgs_futures, timeout=6):
            try:
                res = future.result()
                if res:
                    ddgs_results.extend(res)
            except Exception:
                pass

    if wiki_ev:
        evidence.append(wiki_ev)
    
    seen_urls = set()
    
    for res in ddgs_results:
        url = res.get('href', '')
        if url in seen_urls or 'wikipedia.org' in url.lower():
            continue
        seen_urls.add(url)
        
        title = res.get('title', '').lower()
        body = res.get('body', '').lower()
        text = title + " " + body
        
        # 2. Match Entities and Propositions
        missing_subs = [s for s in subs if s not in text]
        missing_objs = [o for o in objs if o not in text]
        
        if missing_subs and missing_objs and len(subs) > 0 and len(objs) > 0:
            continue # IRRELEVANT
            
        if "manager" in query_text.lower() and "manager" not in text:
            continue
            
        relationship = "CONTEXTUAL"
        
        # 3. Explicit Contradiction
        contradiction_patterns = [
            r'\b(false|fake|debunked|hoax|misleading|unfounded|myth|untrue|conspiracy)\b',
            r'\b(no evidence)\b',
            r'\b(is not)\b',
            r'\b(did not)\b',
            r'\b(never)\b',
            r'\b(not true)\b',
            r'\b(wrong)\b'
        ]
        
        # 4. Explicit Support
        support_patterns = [
            r'\b(true|accurate|confirm|confirmed|verified|proven|fact)\b',
            r'\b(is true)\b',
            r'\b(is indeed)\b'
        ]
        
        is_contradicted = any(re.search(pat, text) for pat in contradiction_patterns)
        is_supported = any(re.search(pat, text) for pat in support_patterns)
        relation_negated = any(f"not {v}" in text or f"did not {v}" in text or f"never {v}" in text for v in verbs)
        
        clean_claim = re.sub(r'[^\w\s]', '', query_text.lower())
        clean_text = re.sub(r'[^\w\s]', '', text)
        exact_match = clean_claim in clean_text
        
        # Determine explicit SUPPORT vs CONTRADICTION
        # Very short claims like "The Sun is a star." matched closely in text
        all_words = set(clean_claim.split())
        words_found = len([w for w in all_words if w in clean_text.split()])
        mostly_matched = (words_found / len(all_words) >= 0.7) if all_words else False
        
        if (exact_match or mostly_matched) and not is_contradicted and not relation_negated:
            relationship = "DIRECT_SUPPORT"
        elif is_contradicted or relation_negated:
            relationship = "DIRECT_CONTRADICTION"
        elif is_supported and mostly_matched:
            relationship = "DIRECT_SUPPORT"
        elif all(v in text for v in verbs) and not is_contradicted:
            if len(verbs) > 0 and (len(subs) > 0 or len(objs) > 0):
                if not missing_subs and not missing_objs:
                    relationship = "DIRECT_SUPPORT"
        
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
            retrieved_at=datetime.utcnow().isoformat() + "Z",
            citation_type="Article",
            evidence_excerpt=res.get('body', '')[:300]
        ))
        
        if len(evidence) >= 8:
            break
            
    return evidence if evidence else []
