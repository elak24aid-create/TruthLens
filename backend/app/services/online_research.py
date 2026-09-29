import os
import re
import math
import time
import requests
import urllib.parse
from typing import List, Dict, Optional, Any
from datetime import datetime
from functools import lru_cache
from duckduckgo_search import DDGS
from concurrent.futures import ThreadPoolExecutor
import spacy
from app.schemas.common import EvidenceItem

try:
    nlp = spacy.load("en_core_web_sm")
except:
    nlp = None

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def search_ddgs(query: str, max_results: int = 5) -> List[Dict]:
    results = []
    for _ in range(3):
        try:
            with DDGS() as ddgs:
                for res in ddgs.text(query, max_results=max_results):
                    results.append(res)
                return results
        except Exception:
            time.sleep(2)
    return results

def search_wiki(query: str, limit: int = 3) -> List[Dict]:
    try:
        # Extract keywords for wiki search to avoid exact sentence misses
        doc = nlp(query) if nlp else None
        if doc:
            keywords = " ".join([t.text for t in doc if t.pos_ in ["NOUN", "PROPN", "ADJ", "VERB"]][:5])
        else:
            keywords = query
        if not keywords: keywords = query
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(keywords)}&utf8=&format=json"
        headers = {'User-Agent': 'TruthLens/1.0 (https://truthlens.com; contact@truthlens.com)'}
        res = requests.get(url, headers=headers, timeout=5).json()
        results = []
        for item in res.get("query", {}).get("search", [])[:limit]:
            snippet = re.sub(r'<[^>]+>', '', item.get("snippet", ""))
            results.append({
                "title": item.get("title", ""),
                "body": snippet,
                "href": f"https://en.wikipedia.org/wiki/{urllib.parse.quote(item.get('title', ''))}"
            })
        return results
    except:
        return []

def evaluate_math(claim: str) -> Optional[bool]:
    math_match = re.search(r'^([0-9\s\+\-\*\/\(\)\.]+)\s*=\s*([0-9\.\-]+)$', claim)
    if math_match:
        try:
            left = eval(math_match.group(1))
            right = float(math_match.group(2))
            return abs(left - right) < 1e-5
        except:
            pass
    return None

def extract_numbers(text):
    return [float(x) for x in re.findall(r'\b\d+(?:\.\d+)?\b', text)]

def check_comparatives(claim_doc, sent_doc, claim, sent):
    # If the claim contains antonyms of what the sentence has
    antonyms = {
        "larger": ["smaller", "less"], "smaller": ["larger", "greater", "bigger"],
        "faster": ["slower"], "slower": ["faster"],
        "taller": ["shorter"], "shorter": ["taller", "higher"],
        "heavier": ["lighter"], "lighter": ["heavier"],
        "hotter": ["colder", "cooler"], "colder": ["hotter", "warmer"],
        "longest": ["shortest"], "shortest": ["longest"],
        "largest": ["smallest"], "smallest": ["largest"],
        "highest": ["lowest"], "lowest": ["highest"]
    }
    for word in claim_doc:
        w = word.text.lower()
        if w in antonyms:
            for ant in antonyms[w]:
                if ant in sent.lower():
                    return True # contradiction found
    return False

def nlp_fallback_verification(claim: str, evidence_texts: List[str]) -> str:
    if not nlp: return "Insufficient Evidence"
    
    doc = nlp(claim)
    claim_lemmas = set([t.lemma_.lower() for t in doc if t.is_alpha and not t.is_stop])
    
    is_neg = any(t.dep_ == "neg" or t.text.lower() in ["not", "never", "no"] for t in doc)
    
    # Extract entities
    strict_ents = [ent.text.lower() for ent in doc.ents if ent.label_ in ["GPE", "LOC", "PERSON", "ORG"]]
    
    # Extract SVO
    subjs, verbs, objs = [], [], []
    for w in doc:
        if "subj" in w.dep_: subjs.append(w.lemma_.lower())
        elif "obj" in w.dep_ or "attr" in w.dep_ or "acomp" in w.dep_: objs.append(w.lemma_.lower())
        elif w.pos_ == "VERB" or w.pos_ == "AUX": verbs.append(w.lemma_.lower())
        
    # Comparatives
    comparatives = [w.text.lower() for w in doc if w.pos_ == "ADJ" and w.text.lower().endswith("er")]
    comparatives += ["more", "less", "larger", "smaller", "faster", "slower", "taller", "shorter", "heavier", "lighter", "hotter", "colder"]
    claim_comps = [c for c in comparatives if c in claim.lower()]
    
    combined = " ".join(evidence_texts)
    sentences = re.split(r'[.!?|\n]', combined)
    
    supported = False
    refuted = False
    
    claim_nums = [float(x) for x in re.findall(r'\b\d+(?:\.\d+)?\b', claim)]
    
    for sent in sentences:
        sent = sent.lower()
        if len(sent.split()) < 3: continue
        
        # Check strict entity co-occurrence and comparative directionality
        # ONLY trigger support if it explicitly matches the relationship
        if claim_comps and subjs and objs:
            e1, e2 = subjs[0], objs[0]
            if e1 in sent and e2 in sent:
                c_idx1, c_idx2 = claim.lower().find(e1), claim.lower().find(e2)
                s_idx1, s_idx2 = sent.find(e1), sent.find(e2)
                
                claim_order = c_idx1 < c_idx2
                sent_order = s_idx1 < s_idx2
                
                has_comp = any(c in sent for c in claim_comps)
                
                antonyms = {"heavier": ["lighter"], "lighter": ["heavier"], "larger": ["smaller"], "smaller": ["larger"], "faster": ["slower"], "slower": ["faster"], "taller": ["shorter"], "shorter": ["taller"], "hotter": ["colder"], "colder": ["hotter"], "more": ["less"], "less": ["more"]}
                has_ant = any(ant in sent for comp in claim_comps for ant in antonyms.get(comp, []))
                
                if has_comp:
                    if claim_order != sent_order:
                        refuted = True
                    else:
                        supported = True
                
                if has_ant:
                    if claim_order == sent_order:
                        refuted = True
                    else:
                        supported = True
                        
                if refuted or supported:
                    continue
                else:
                    # If it's a comparative claim and entities co-occur but there's no comparative adjective, it's unrelated!
                    continue
            else:
                # Entities don't co-occur in the sentence, it's not support for comparative
                continue
                
        # General SVO relationship check
        sent_doc = nlp(sent)
        sent_lemmas = set([t.lemma_.lower() for t in sent_doc if t.is_alpha])
        overlap = len(claim_lemmas.intersection(sent_lemmas))
        if overlap >= 2:
            if subjs and objs and is_neg:
                svo_found = False
                for t in sent_doc:
                    if t.pos_ in ["VERB", "AUX"] or t.lemma_.lower() == 'be':
                        kids = [c.lemma_.lower() for c in t.children]
                        # For true SVO, the subject and object must be direct dependents of the same verb
                        if any(s in kids for s in subjs) and any(o in kids for o in objs):
                            svo_found = True
                            break
                if not svo_found:
                    continue
                
            sent_nums = [float(x) for x in re.findall(r'\b\d+(?:\.\d+)?\b', sent)]
            num_contradiction = False
            if claim_nums and sent_nums:
                if not any(c in sent_nums for c in claim_nums):
                    num_contradiction = True
                    
            has_sent_neg = any(t.dep_ == "neg" or t.text.lower() in ["not", "never", "cannot", "no"] for t in sent_doc)
            
            if num_contradiction:
                refuted = True
            elif has_sent_neg:
                refuted = True
            else:
                supported = True

    if refuted:
         return "Likely Misleading" if not is_neg else "Likely Genuine"
    if supported:
         return "Likely Genuine" if not is_neg else "Likely Misleading"
         
    if len(strict_ents) > 0:
        if claim_comps and not supported and not refuted:
            return "Insufficient Evidence"
        return "Likely Genuine" if not is_neg else "Likely Misleading"
         
    if is_neg and not supported and not refuted:
        return "Likely Genuine"
        
    return "Insufficient Evidence"

def use_gemini_verification(claim: str, evidence: List[Dict]) -> str:
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        context = "\n".join([f"Source: {e['body']}" for e in evidence])
        prompt = f"""
You are a strict fact-checking engine.
Claim: "{claim}"
Evidence:
{context}

Based ONLY on the evidence provided above, verify the claim.
Rules:
1. If the evidence strongly supports the claim, output exactly: LIKELY_GENUINE
2. If the evidence strongly contradicts or refutes the claim, output exactly: LIKELY_MISLEADING
3. If the evidence is insufficient to verify the claim, output exactly: INSUFFICIENT_EVIDENCE
Do not output anything else.
"""
        res = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        text = res.text.strip().upper()
        if "GENUINE" in text: return "Likely Genuine"
        if "MISLEADING" in text: return "Likely Misleading"
        return "Insufficient Evidence"
    except Exception as e:
        print(f"Gemini error: {e}")
        return "Error"

@lru_cache(maxsize=100)
def perform_online_research(claim: str) -> Optional[List[EvidenceItem]]:
    query_text = re.sub(r'http\S+', '', claim).strip()
    if not query_text:
        return []
        
    evidence_items = []
    
    # 1. Math Check (Stage 7)
    math_res = evaluate_math(query_text)
    if math_res is not None:
        rel = "DIRECT_SUPPORT" if math_res else "DIRECT_CONTRADICTION"
        evidence_items.append(EvidenceItem(
            source_type="computational",
            publisher="Math Evaluator",
            title="Calculation Verification",
            url="local://math",
            domain="local",
            relationship=rel,
            published_date=datetime.utcnow().isoformat() + "Z",
            retrieved_at=datetime.utcnow().isoformat() + "Z",
            citation_type="Calculation",
            evidence_excerpt=f"Mathematical evaluation of '{query_text}' is {math_res}."
        ))
        return evidence_items

    # 4. Multi-Source Retrieval
    ddgs_results = search_ddgs(query_text, max_results=4)
    wiki_results = search_wiki(query_text, limit=4)
    
    all_raw_evidence = ddgs_results + wiki_results
    if not all_raw_evidence:
        return []

    # Format for NLP fallback
    evidence_texts = [e.get("body", "") for e in all_raw_evidence if e.get("body")]
    
    if GEMINI_API_KEY:
        verdict = use_gemini_verification(query_text, all_raw_evidence)
    else:
        verdict = nlp_fallback_verification(query_text, evidence_texts)
        
    rel_map = {
        "Likely Genuine": "DIRECT_SUPPORT",
        "Likely Misleading": "DIRECT_CONTRADICTION",
        "Insufficient Evidence": "CONTEXTUAL"
    }
    
    final_rel = rel_map.get(verdict, "CONTEXTUAL")

    for raw in all_raw_evidence:
        domain = urllib.parse.urlparse(raw.get("href", "")).netloc.replace("www.", "")
        if not domain:
            domain = "wikipedia.org"
            
        evidence_items.append(EvidenceItem(
            source_type="web",
            publisher=domain.split('.')[0].title(),
            title=raw.get("title", "Search Result")[:100],
            url=raw.get("href", ""),
            domain=domain,
            relationship=final_rel,
            published_date=datetime.utcnow().isoformat() + "Z",
            retrieved_at=datetime.utcnow().isoformat() + "Z",
            citation_type="Article",
            evidence_excerpt=(raw.get("body", "")[:400] + "...") if raw.get("body") else ""
        ))
        
    return evidence_items
