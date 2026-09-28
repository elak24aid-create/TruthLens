import re

with open("backend/app/services/online_research.py", "r") as f:
    content = f.read()

new_ddgs = """    search_queries = [query_text]
    
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
                
            relationship = "context"
            
            high_quality = ['nasa.gov', 'wikipedia.org', 'britannica.com', 'edu', 'gov', 'reuters.com', 'apnews.com', 'bbc.com', 'snopes.com', 'politifact.com', 'factcheck.org', 'nature.com']
            is_high_quality = any(hq in url.lower() for hq in high_quality)
            
            contradiction_patterns = [
                r'\\b(false|fake|debunked|hoax|misleading|unfounded|myth|untrue)\\b',
                r'\\b(no evidence)\\b',
                r'\\b(is not)\\b',
                r'\\b(did not)\\b',
                r'\\b(never)\\b',
                r'\\b(conspiracy)\\b',
                r'\\b(incorrect)\\b',
                r'\\b(wrong)\\b'
            ]
            
            support_patterns = [
                r'\\b(true|accurate|confirm|confirmed|verified|proven|fact)\\b',
                r'\\b(is true)\\b'
            ]
            
            is_contradicted = any(re.search(pat, text) for pat in contradiction_patterns)
            is_supported = any(re.search(pat, text) for pat in support_patterns)
            relation_negated = any(f"not {v}" in text or f"did not {v}" in text or f"never {v}" in text for v in verbs)
            
            clean_claim_words = set(re.findall(r'\\w+', query_text.lower()))
            clean_text_words = set(re.findall(r'\\w+', text))
            overlap = clean_claim_words.intersection(clean_text_words)
            
            if is_high_quality and not is_contradicted and (len(overlap) >= len(clean_claim_words)*0.4):
                is_supported = True
                
            if is_contradicted or relation_negated:
                relationship = "conflicting"
            elif is_supported:
                relationship = "supporting"
                
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
        logger.error(f"Online research failed: {e}")"""

start_idx = content.find("    search_queries = [")
end_idx = content.rfind("return evidence")

content = content[:start_idx] + new_ddgs + "\n    " + content[end_idx:]

with open("backend/app/services/online_research.py", "w") as f:
    f.write(content)
