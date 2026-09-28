from concurrent.futures import ThreadPoolExecutor, as_completed
import spacy
from typing import List, Optional
from ddgs import DDGS
from app.schemas.common import EvidenceItem
from datetime import datetime
import re
from functools import lru_cache
import logging
import requests

logger = logging.getLogger(__name__)

try:
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    logger.error(f"Failed to load spacy model: {e}")
    nlp = None

def get_wiki_summary(query: str) -> str:
    headers = {'User-Agent': 'TruthLensBot/1.0 (contact@truthlens.com)'}
    try:
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&utf8=&format=json"
        s_res = requests.get(search_url, headers=headers, timeout=5).json()
        search = s_res.get('query', {}).get('search', [])
        if not search:
            return ""
        title = search[0]['title']
        url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=true&explaintext=true&format=json&titles={title}"
        res = requests.get(url, headers=headers, timeout=5).json()
        pages = res.get('query', {}).get('pages', {})
        for page_id in pages:
            if str(page_id) != "-1":
                return pages[page_id].get('extract', '').lower()
    except Exception:
        pass
    return ""

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
            
        summary = get_wiki_summary(subj)
        if not summary:
            return None
            
        # Use word boundaries for exact match
        has_attr = bool(re.search(r'\b' + re.escape(attr_core) + r'\b', summary))
        
        rel = "DIRECT_SUPPORT" if has_attr else "DIRECT_CONTRADICTION"
        
        # If the claim is flat Earth, specifically handle missing flat
        if not has_attr and attr_core in ['flat', 'president', 'ceo', 'dead', 'alive', 'king', 'queen', 'founder', 'inventor']:
            return EvidenceItem(
                source_type="web_search",
                publisher="wikipedia",
                title=f"Wikipedia: {subj.title()}",
                url=f"https://en.wikipedia.org/wiki/{subj.replace(' ', '_')}",
                domain="wikipedia.org",
                relationship=rel,
                published_date=None,
                retrieved_at=datetime.now().isoformat(),
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
    # Looks for a simple equation like "X + Y = Z"
    math_match = re.search(r'^([0-9\s\+\-\*\/\(\)\.]+)\s*=\s*([0-9\.\-]+)$', query_text)
    if math_match:
        left_expr = math_match.group(1).strip()
        right_val = math_match.group(2).strip()
        try:
            # Safely evaluate basic math
            # Filter out any malicious builtins by restricting globals/locals
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
        
    wiki_ev = check_identity(query_text)
    if wiki_ev:
        evidence.append(wiki_ev)
        
    svo = extract_svo(query_text)
    subs = set(svo["subjects"])
    objs = set(svo["objects"])
    verbs = set(svo["verbs"])
    
    # 1. Search for exact claim and fact checks
    search_queries = [query_text]
    
    seen_urls = set()
    evidence_results = []
    
    def fetch_ddgs(q):
        try:
            with DDGS() as ddgs:
                return list(ddgs.text(q, max_results=5))
        except:
            return []
            
    try:
        from concurrent.futures import ThreadPoolExecutor, as_completed
        results = []
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(fetch_ddgs, q) for q in search_queries]
            for future in as_completed(futures, timeout=10):
                try:
                    results.extend(future.result())
                except:
                    pass
                    
        for res in results:
            url = res.get('href', '')
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            
            title = res.get('title', '').lower()
            body = res.get('body', '').lower()
            text = title + " " + body
            
            missing_subs = [s for s in subs if s not in text]
            missing_objs = [o for o in objs if o not in text]
            
            if missing_subs and missing_objs and len(subs) > 0 and len(objs) > 0:
                continue
                
            relationship = "CONTEXTUAL"
            
            high_quality = ['nasa.gov', 'wikipedia.org', 'britannica.com', 'edu', 'gov', 'reuters.com', 'apnews.com', 'bbc.com', 'snopes.com', 'politifact.com', 'factcheck.org', 'nature.com']
            is_high_quality = any(hq in url.lower() for hq in high_quality)
            
            contradiction_patterns = [
                r'\b(false|fake|debunked|hoax|misleading|unfounded|myth|untrue)\b',
                r'\b(no evidence)\b',
                r'\b(is not)\b',
                r'\b(did not)\b',
                r'\b(never)\b',
                r'\b(conspiracy)\b',
                r'\b(incorrect)\b',
                r'\b(wrong)\b'
            ]
            
            support_patterns = [
                r'\b(true|accurate|confirm|confirmed|verified|proven|fact)\b',
                r'\b(is true)\b'
            ]
            
            is_contradicted = any(re.search(pat, text) for pat in contradiction_patterns)
            is_supported = any(re.search(pat, text) for pat in support_patterns)
            relation_negated = any(f"not {v}" in text or f"did not {v}" in text or f"never {v}" in text for v in verbs)
            
            clean_claim_words = set(re.findall(r'\w+', query_text.lower()))
            clean_text_words = set(re.findall(r'\w+', text))
            overlap = clean_claim_words.intersection(clean_text_words)
            
            if is_high_quality and not is_contradicted and (len(overlap) >= len(clean_claim_words)*0.4):
                is_supported = True
                
            if is_contradicted or relation_negated:
                relationship = "DIRECT_CONTRADICTION"
            elif is_supported:
                relationship = "DIRECT_SUPPORT"
                
            source = url.split('/')[2] if url else 'Unknown'
            if source.startswith('www.'):
                source = source[4:]
                
            evidence_results.append(EvidenceItem(
                source_type="web_search",
                publisher=source,
                title=res.get('title', '')[:150],
                url=url,
                domain=source,
                relationship=relationship,
                published_date=datetime.utcnow().isoformat() + "Z",
                retrieved_at=datetime.utcnow().isoformat() + "Z",
                citation_type="Article",
                evidence_excerpt=res.get('body', '')[:300]
            ))
            
            if len(evidence_results) >= 5:
                break
        evidence.extend(evidence_results)
    except Exception as e:
        logger.error(f"Online research failed: {e}")
    return evidence
