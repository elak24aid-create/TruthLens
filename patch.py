import re

with open("backend/app/services/online_research.py", "r") as f:
    content = f.read()

# Replace DDGS logic
new_ddgs = """    search_queries = [query_text]
    
    seen_urls = set()
    evidence_results = []
    
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(search_queries[0], max_results=5))
            for res in results:
                url = res.get('href', '')
                if not url or url in seen_urls: continue
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
                
                clean_claim = re.sub(r'[^\\w\\s]', '', query_text.lower())
                clean_text = re.sub(r'[^\\w\\s]', '', text)
                exact_match = clean_claim in clean_text
                
                if is_high_quality and not is_contradicted and (len(overlap) >= len(clean_claim_words)*0.4):
                    is_supported = True
                
                if is_contradicted or relation_negated:
                    relationship = "conflicting"
                elif exact_match and not is_contradicted and not relation_negated:
                    relationship = "supporting"
                elif is_supported:
                    relationship = "supporting"
                elif all(v in text for v in verbs) and not is_contradicted:
                    if len(verbs) > 0 and (len(subs) > 0 or len(objs) > 0):
                        if not missing_subs and not missing_objs:
                            relationship = "supporting"
                
                source = url.split('/')[2] if url else 'Unknown'
                if source.startswith('www.'):
                    source = source[4:]
                    
                evidence_results.append(EvidenceItem(
                    source_type="web_search",
                    publisher=source,
                    title=res.get('title', 'Web Result')[:100],
                    url=url,
                    domain=source,
                    relationship=relationship,
                    published_date=datetime.utcnow().isoformat() + "Z",
                    retrieved_at=datetime.utcnow().isoformat() + "Z",
                    citation_type="Article",
                    evidence_excerpt=body[:400] + "..."
                ))
            
            evidence.extend(evidence_results)
    except Exception as e:
        print("DDGS Error:", e)"""

content = re.sub(r'search_queries = \[.*?except Exception as e:.*?print.*?\n', new_ddgs + '\n', content, flags=re.DOTALL)
with open("backend/app/services/online_research.py", "w") as f:
    f.write(content)
