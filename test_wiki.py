import requests

headers = {
    'User-Agent': 'TruthLensBot/1.0 (test@example.com)'
}

def get_wiki_summary(query):
    url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=true&explaintext=true&format=json&titles={query}"
    res = requests.get(url, headers=headers).json()
    pages = res.get('query', {}).get('pages', {})
    for page_id in pages:
        if str(page_id) != "-1":
            return pages[page_id].get('extract', '')
    
    # If not found, try searching first
    search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&utf8=&format=json"
    s_res = requests.get(search_url, headers=headers).json()
    search = s_res.get('query', {}).get('search', [])
    if search:
        title = search[0]['title']
        return get_wiki_summary(title)
    return ""

print("Michael Jackson:")
print(get_wiki_summary("Michael Jackson"))
print("\nEarth:")
print(get_wiki_summary("Earth"))
