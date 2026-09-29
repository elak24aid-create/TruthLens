import requests
import json

url = "https://truthlens-l1vq.onrender.com/api/news"
news = requests.get(url).json()

urls_to_test = ['https://en.wikipedia.org/wiki/Earth']
if 'articles' in news and len(news['articles']) >= 2:
    urls_to_test.append(news['articles'][0]['url'])
    urls_to_test.append(news['articles'][1]['url'])

for u in urls_to_test:
    print(f"Testing URL: {u}")
    res = requests.post("https://truthlens-l1vq.onrender.com/api/check-url", json={'url': u}).json()
    print(f"VERDICT: {res.get('verdict', res)}")
    print("CLAIM:", res.get('metadata', {}).get('claims_found', [''])[0] if res.get('metadata') else res)
    print("EVIDENCE COUNT:", len(res.get('evidence', [])))
    print("SOURCES:", [ev.get('domain') for ev in res.get('evidence', [])])
    print("---")
