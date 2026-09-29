import re

with open('backend/app/services/online_research.py', 'r') as f:
    content = f.read()

wikipedia_fallback = """
def search_wikipedia_fulltext(query: str, limit: int = 3) -> list:
    import urllib.parse, requests, re
    q = urllib.parse.quote(query)
    url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={q}&utf8=&format=json"
    results = []
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5).json()
        for item in res.get('query', {}).get('search', [])[:limit]:
            snippet = re.sub(r'<[^>]+>', '', item.get('snippet', ''))
            results.append({
                'title': item.get('title', ''),
                'body': snippet,
                'href': f"https://en.wikipedia.org/wiki/{urllib.parse.quote(item.get('title', ''))}"
            })
    except Exception:
        pass
    return results

"""

if "def search_wikipedia_fulltext" not in content:
    content = content.replace("def search_ddgs", wikipedia_fallback + "def search_ddgs")

replacement = """    if not ddgs_results and not wiki_ev and errors:
        # Fallback to Wikipedia Fulltext
        wiki_results = search_wikipedia_fulltext(query_text, 3)
        if wiki_results:
            ddgs_results.extend(wiki_results)
            errors = []
        else:
            raise Exception("Search engine failure or timeout.")"""

content = content.replace('    if not ddgs_results and not wiki_ev and errors:\n        raise Exception("Search engine failure or timeout.")', replacement)

exact_match_fix = """
        clean_claim = re.sub(r'[^\\w\\s]', '', query_text.lower())
        clean_text = re.sub(r'[^\\w\\s]', '', text)
        exact_match = clean_claim in clean_text
        
        # Determine explicit SUPPORT vs CONTRADICTION
        matched_keywords = set(w for w in subs + objs if w in text)
        mostly_matched = len(matched_keywords) >= len(set(subs + objs)) * 0.5
        
        if exact_match and not is_contradicted:
            rel = "DIRECT_SUPPORT"
        elif mostly_matched and (is_supported or is_contradicted):"""

content = content.replace("""        clean_claim = re.sub(r'[^\\w\\s]', '', query_text.lower())
        clean_text = re.sub(r'[^\\w\\s]', '', text)
        exact_match = clean_claim in clean_text
        
        # Determine explicit SUPPORT vs CONTRADICTION
        matched_keywords = set(w for w in subs + objs if w in text)
        mostly_matched = len(matched_keywords) >= len(set(subs + objs)) * 0.5
        
        if mostly_matched and (is_supported or is_contradicted):""", exact_match_fix)

with open('backend/app/services/online_research.py', 'w') as f:
    f.write(content)
